"""Serviço de aplicação do agregado `Client` (regras de negócio sobre o repositório da Fase 5)."""

from __future__ import annotations

from time import perf_counter
from uuid import UUID

from fastapi_cache.decorator import cache

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.mapper.client_mapper import ClientMapper
from energyhub.clients.domain.exception.client_already_exists_exception import (
    ClientAlreadyExistsException,
)
from energyhub.clients.domain.exception.client_not_found_exception import ClientNotFoundException
from energyhub.clients.infrastructure.messaging.client_event_producer import ClientEventProducer
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.cache_constants import CacheConstants
from energyhub.shared.infrastructure.cache.cache_config import id_key_builder, page_key_builder
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_cache
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.metrics.business_metrics import business_metrics, record_safely


class ClientService:
    """CRUD de clientes com checagens de existência/unicidade. Faz `flush` via repositório;
    o `commit` fica com a sessão por requisição (`get_session`).

    Após cada escrita persistida publica o evento de cliente (RabbitMQ) como efeito colateral
    não-bloqueante — uma falha de broker é logada, não desfaz a escrita. A criação também registra
    métricas Prometheus (duração + `client_created_total`), de forma livre de falhas.
    """

    def __init__(
        self,
        repository: ClientRepository,
        mapper: ClientMapper | None = None,
        event_producer: ClientEventProducer | None = None,
    ) -> None:
        self._repository = repository
        self._mapper = mapper or ClientMapper()
        self._producer = event_producer

    async def create(self, dto: ClientRequestDTO) -> ClientResponseDTO:
        start = perf_counter()
        if await self._repository.exists_by_cnpj(dto.cnpj):
            raise ClientAlreadyExistsException(f"Já existe um cliente com o CNPJ {dto.cnpj}")
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CLIENTS)
        response = self._mapper.to_response_dto(saved)
        if self._producer is not None:
            await publish_safely(
                self._producer.publish_client_created(response), event="client.created"
            )
        elapsed = perf_counter() - start
        record_safely(lambda: business_metrics.observe_operation("client_create", "POST", elapsed))
        record_safely(business_metrics.increment_client_created)
        return response

    @cache(
        namespace=CacheConstants.CLIENTS,
        expire=CacheConstants.SHORT_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_id(self, client_id: UUID) -> ClientResponseDTO:
        entity = await self._repository.find_by_id(client_id)
        if entity is None:
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    @cache(
        namespace=CacheConstants.CLIENTS,
        expire=CacheConstants.SHORT_TTL,
        key_builder=page_key_builder,
    )
    async def find_all(self, page_request: PageRequest) -> PageResponse[ClientResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, client_id: UUID, dto: ClientRequestDTO) -> ClientResponseDTO:
        entity = await self._repository.find_by_id(client_id)
        if entity is None:
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        entity.corporate_name = dto.corporate_name
        entity.trade_name = dto.trade_name
        entity.email = dto.email
        entity.phone = dto.phone
        entity.address = dto.address
        entity.city = dto.city
        entity.state = dto.state
        entity.zip_code = dto.zip_code
        entity.active = dto.active
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CLIENTS)
        response = self._mapper.to_response_dto(saved)
        if self._producer is not None:
            await publish_safely(
                self._producer.publish_client_updated(response), event="client.updated"
            )
        return response

    async def delete(self, client_id: UUID) -> None:
        if not await self._repository.exists_by_id(client_id):
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        await self._repository.delete_by_id(client_id)
        await invalidate_cache(CacheConstants.CLIENTS)
