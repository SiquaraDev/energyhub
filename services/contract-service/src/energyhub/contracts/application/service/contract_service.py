"""Serviço de aplicação do agregado `Contract` (regras de negócio sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from fastapi_cache.decorator import cache

from energyhub.contracts.application.dto.contract_request_dto import ContractRequestDTO
from energyhub.contracts.application.dto.contract_response_dto import ContractResponseDTO
from energyhub.contracts.application.mapper.contract_mapper import ContractMapper
from energyhub.contracts.domain.exception.contract_already_exists_exception import (
    ContractAlreadyExistsException,
)
from energyhub.contracts.domain.exception.contract_not_found_exception import (
    ContractNotFoundException,
)
from energyhub.contracts.infrastructure.persistence.contract_repository import ContractRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.cache_constants import CacheConstants
from energyhub.shared.infrastructure.cache.cache_config import id_key_builder, page_key_builder
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_cache
from energyhub.shared.infrastructure.messaging.kafka_config import KafkaConfig
from energyhub.shared.infrastructure.messaging.kafka_event_producer import KafkaEventProducer
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.metrics.business_metrics import business_metrics, record_safely


class ContractService:
    """CRUD de contratos com checagens de existência/unicidade. Faz `flush` via repositório;
    o `commit` fica com a sessão por requisição (`get_session`).

    Contratos são eventos de alto volume: após cada escrita, publica no tópico Kafka
    `contract-events` sob a chave = id do contrato (mesma chave → mesma partição, ordem preservada),
    como efeito colateral não-bloqueante.
    """

    def __init__(
        self,
        repository: ContractRepository,
        mapper: ContractMapper | None = None,
        kafka_producer: KafkaEventProducer | None = None,
    ) -> None:
        self._repository = repository
        self._mapper = mapper or ContractMapper()
        self._kafka = kafka_producer

    async def _publish_event(self, response: ContractResponseDTO) -> None:
        """Publica o contrato no tópico `contract-events` (chave = id), se houver produtor."""
        if self._kafka is not None:
            await publish_safely(
                self._kafka.publish(
                    KafkaConfig.CONTRACT_EVENTS,
                    str(response.id),
                    response.model_dump(mode="json"),
                ),
                event=KafkaConfig.CONTRACT_EVENTS,
            )

    async def create(self, dto: ContractRequestDTO) -> ContractResponseDTO:
        if await self._repository.exists_by_contract_number(dto.contract_number):
            raise ContractAlreadyExistsException(
                f"Já existe um contrato com o número {dto.contract_number}"
            )
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CONTRACTS)
        response = self._mapper.to_response_dto(saved)
        await self._publish_event(response)
        record_safely(lambda: business_metrics.increment_contract_created(response.status.value))
        return response

    @cache(
        namespace=CacheConstants.CONTRACTS,
        expire=CacheConstants.DEFAULT_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_id(self, contract_id: UUID) -> ContractResponseDTO:
        entity = await self._repository.find_by_id(contract_id)
        if entity is None:
            raise ContractNotFoundException(f"Contrato {contract_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    @cache(
        namespace=CacheConstants.CONTRACTS,
        expire=CacheConstants.DEFAULT_TTL,
        key_builder=page_key_builder,
    )
    async def find_all(self, page_request: PageRequest) -> PageResponse[ContractResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, contract_id: UUID, dto: ContractRequestDTO) -> ContractResponseDTO:
        entity = await self._repository.find_by_id(contract_id)
        if entity is None:
            raise ContractNotFoundException(f"Contrato {contract_id} não encontrado")
        entity.start_date = dto.start_date
        entity.end_date = dto.end_date
        entity.energy_amount = dto.energy_amount
        entity.unit_price = dto.unit_price
        entity.total_value = dto.total_value
        entity.type = dto.type
        entity.status = dto.status
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CONTRACTS)
        response = self._mapper.to_response_dto(saved)
        await self._publish_event(response)
        return response

    async def delete(self, contract_id: UUID) -> None:
        if not await self._repository.exists_by_id(contract_id):
            raise ContractNotFoundException(f"Contrato {contract_id} não encontrado")
        await self._repository.delete_by_id(contract_id)
        await invalidate_cache(CacheConstants.CONTRACTS)
