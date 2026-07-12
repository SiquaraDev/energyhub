"""Caso de uso: criar fatura."""

from __future__ import annotations

from energyhub.financial.application.dto.invoice_request_dto import InvoiceRequestDTO
from energyhub.financial.application.dto.invoice_response_dto import InvoiceResponseDTO
from energyhub.financial.application.service.invoice_service import InvoiceService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateInvoiceUseCase(UseCase[InvoiceRequestDTO, InvoiceResponseDTO]):
    """Orquestra a criação de uma fatura delegando ao `InvoiceService` (sem lógica própria)."""

    def __init__(self, service: InvoiceService) -> None:
        self._service = service

    async def execute(self, input_data: InvoiceRequestDTO) -> InvoiceResponseDTO:
        return await self._service.create(input_data)
