"""DTO de resposta de pagamento."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from energyhub.shared.application.dto.base_dto import BaseDTO


class PaymentResponseDTO(BaseDTO):
    """Representação de saída de um pagamento (inclui id/timestamps do `BaseDTO`)."""

    invoice_id: UUID = Field(
        ...,
        description="Id da fatura à qual o pagamento pertence",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    amount: Decimal = Field(..., description="Valor pago", examples=["500.00"])
    payment_date: datetime = Field(
        ..., description="Data/hora do pagamento", examples=["2026-08-20T14:30:00"]
    )
