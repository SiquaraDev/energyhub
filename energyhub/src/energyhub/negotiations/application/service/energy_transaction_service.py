"""Serviço de aplicação de transações de energia (sub-recurso de negociação)."""

from __future__ import annotations

from uuid import UUID

from energyhub.negotiations.application.dto.energy_transaction_request_dto import (
    EnergyTransactionRequestDTO,
)
from energyhub.negotiations.application.dto.energy_transaction_response_dto import (
    EnergyTransactionResponseDTO,
)
from energyhub.negotiations.application.mapper.energy_transaction_mapper import (
    EnergyTransactionMapper,
)
from energyhub.negotiations.domain.exception.energy_transaction_not_found_exception import (
    EnergyTransactionNotFoundException,
)
from energyhub.negotiations.infrastructure.persistence.energy_transaction_repository import (
    EnergyTransactionRepository,
)
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class EnergyTransactionService:
    """Cria/consulta transações de energia. Persiste via FK (`negotiation_id` no DTO), sem
    relação ORM. Transações não têm chave de negócio única (sem checagem de unicidade)."""

    def __init__(
        self,
        repository: EnergyTransactionRepository,
        mapper: EnergyTransactionMapper | None = None,
    ) -> None:
        self._repository = repository
        self._mapper = mapper or EnergyTransactionMapper()

    async def create(
        self, negotiation_id: UUID, dto: EnergyTransactionRequestDTO
    ) -> EnergyTransactionResponseDTO:
        entity = self._mapper.to_entity(negotiation_id, dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, transaction_id: UUID) -> EnergyTransactionResponseDTO:
        entity = await self._repository.find_by_id(transaction_id)
        if entity is None:
            raise EnergyTransactionNotFoundException(
                f"Transação de energia {transaction_id} não encontrada"
            )
        return self._mapper.to_response_dto(entity)

    async def find_all(
        self, page_request: PageRequest
    ) -> PageResponse[EnergyTransactionResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def find_by_negotiation_id(
        self, negotiation_id: UUID
    ) -> list[EnergyTransactionResponseDTO]:
        transactions = await self._repository.find_by_negotiation_id(negotiation_id)
        return [self._mapper.to_response_dto(transaction) for transaction in transactions]
