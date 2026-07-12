"""DTO de request de pagamento."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentRequestDTO(BaseModel):
    """Dados de entrada de um pagamento. `invoice_id` vem do path do sub-recurso, não do corpo."""

    amount: Decimal = Field(
        ...,
        gt=0,
        description="Valor pago",
        examples=["500.00"],
    )
    payment_date: datetime = Field(
        ...,
        description="Data/hora do pagamento",
        examples=["2026-08-20T14:30:00"],
    )
