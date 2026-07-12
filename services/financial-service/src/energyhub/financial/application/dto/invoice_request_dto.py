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

    invoice_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Número da fatura (único)",
        examples=["INV-2026-0001"],
    )
    client_id: UUID = Field(
        ...,
        description="Id do cliente da fatura",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    amount: Decimal = Field(
        ...,
        ge=0,
        description="Valor da fatura",
        examples=["1500.00"],
    )
    due_date: date = Field(
        ...,
        description="Data de vencimento",
        examples=["2026-08-15"],
    )
    status: InvoiceStatus = Field(
        InvoiceStatus.DRAFT,
        description="Status da fatura (DRAFT, ISSUED, PAID, ...)",
        examples=["ISSUED"],
    )

    @field_validator("invoice_number")
    @classmethod
    def _validate_invoice_number(cls, value: str) -> str:
        return validate_non_empty(value)
