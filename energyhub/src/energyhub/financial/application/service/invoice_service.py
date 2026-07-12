"""Serviço de aplicação do agregado `Invoice` (regras de negócio sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from energyhub.financial.application.dto.invoice_request_dto import InvoiceRequestDTO
from energyhub.financial.application.dto.invoice_response_dto import InvoiceResponseDTO
from energyhub.financial.application.mapper.invoice_mapper import InvoiceMapper
from energyhub.financial.domain.exception.invoice_already_exists_exception import (
    InvoiceAlreadyExistsException,
)
from energyhub.financial.domain.exception.invoice_not_found_exception import (
    InvoiceNotFoundException,
)
from energyhub.financial.infrastructure.persistence.invoice_repository import InvoiceRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class InvoiceService:
    """CRUD de faturas com checagem de unicidade do número. Faz `flush` via repositório;
    o `commit` fica com a sessão por requisição (`get_session`)."""

    def __init__(self, repository: InvoiceRepository, mapper: InvoiceMapper | None = None) -> None:
        self._repository = repository
        self._mapper = mapper or InvoiceMapper()

    async def create(self, dto: InvoiceRequestDTO) -> InvoiceResponseDTO:
        if await self._repository.exists_by_invoice_number(dto.invoice_number):
            raise InvoiceAlreadyExistsException(
                f"Já existe uma fatura com o número {dto.invoice_number}"
            )
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, invoice_id: UUID) -> InvoiceResponseDTO:
        entity = await self._repository.find_by_id(invoice_id)
        if entity is None:
            raise InvoiceNotFoundException(f"Fatura {invoice_id} não encontrada")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[InvoiceResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, invoice_id: UUID, dto: InvoiceRequestDTO) -> InvoiceResponseDTO:
        entity = await self._repository.find_by_id(invoice_id)
        if entity is None:
            raise InvoiceNotFoundException(f"Fatura {invoice_id} não encontrada")
        entity.amount = dto.amount
        entity.due_date = dto.due_date
        entity.status = dto.status
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def delete(self, invoice_id: UUID) -> None:
        if not await self._repository.exists_by_id(invoice_id):
            raise InvoiceNotFoundException(f"Fatura {invoice_id} não encontrada")
        await self._repository.delete_by_id(invoice_id)
