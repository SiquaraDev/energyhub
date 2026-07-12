"""DTO de request de fatura."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.shared.application.validation.validators import validate_non_empty


class InvoiceRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar uma fatura."""

    invoice_number: str = Field(..., description="Número da fatura (único)")
    client_id: UUID = Field(..., description="Id do cliente da fatura")
    amount: Decimal = Field(..., description="Valor da fatura")
    due_date: date = Field(..., description="Data de vencimento")
    status: InvoiceStatus = Field(
        InvoiceStatus.DRAFT, description="Status da fatura (DRAFT, ISSUED, PAID, ...)"
    )

    @field_validator("invoice_number")
    @classmethod
    def _validate_invoice_number(cls, value: str) -> str:
        return validate_non_empty(value)
