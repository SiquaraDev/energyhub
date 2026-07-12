"""Serviço de aplicação do agregado `Negotiation` (regras sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from energyhub.negotiations.application.dto.negotiation_request_dto import NegotiationRequestDTO
from energyhub.negotiations.application.dto.negotiation_response_dto import NegotiationResponseDTO
from energyhub.negotiations.application.mapper.negotiation_mapper import NegotiationMapper
from energyhub.negotiations.domain.exception.negotiation_not_found_exception import (
    NegotiationNotFoundException,
)
from energyhub.negotiations.infrastructure.persistence.negotiation_repository import (
    NegotiationRepository,
)
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class NegotiationService:
    """CRUD de negociações. Faz `flush` via repositório; o `commit` fica com a sessão
    por requisição (`get_session`). Negociações não têm chave de negócio única."""

    def __init__(
        self, repository: NegotiationRepository, mapper: NegotiationMapper | None = None
    ) -> None:
        self._repository = repository
        self._mapper = mapper or NegotiationMapper()

    async def create(self, dto: NegotiationRequestDTO) -> NegotiationResponseDTO:
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, negotiation_id: UUID) -> NegotiationResponseDTO:
        entity = await self._repository.find_by_id(negotiation_id)
        if entity is None:
            raise NegotiationNotFoundException(f"Negociação {negotiation_id} não encontrada")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[NegotiationResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(
        self, negotiation_id: UUID, dto: NegotiationRequestDTO
    ) -> NegotiationResponseDTO:
        entity = await self._repository.find_by_id(negotiation_id)
        if entity is None:
            raise NegotiationNotFoundException(f"Negociação {negotiation_id} não encontrada")
        entity.status = dto.status
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def delete(self, negotiation_id: UUID) -> None:
        if not await self._repository.exists_by_id(negotiation_id):
            raise NegotiationNotFoundException(f"Negociação {negotiation_id} não encontrada")
        await self._repository.delete_by_id(negotiation_id)
