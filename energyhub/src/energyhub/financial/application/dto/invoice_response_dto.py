"""DTO de resposta de fatura."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class InvoiceResponseDTO(BaseDTO):
    """Representação de saída de uma fatura (inclui id/timestamps do `BaseDTO`)."""

    invoice_number: str = Field(
        ..., description="Número da fatura (único)", examples=["INV-2026-0001"]
    )
    client_id: UUID = Field(
        ...,
        description="Id do cliente da fatura",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    amount: Decimal = Field(..., description="Valor da fatura", examples=["1500.00"])
    due_date: date = Field(..., description="Data de vencimento", examples=["2026-08-15"])
    status: InvoiceStatus = Field(
        ..., description="Status da fatura (DRAFT, ISSUED, PAID, ...)", examples=["ISSUED"]
    )
