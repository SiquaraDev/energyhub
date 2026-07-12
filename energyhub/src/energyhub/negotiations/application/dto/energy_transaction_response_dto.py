"""DTO de resposta de transação de energia."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.shared.application.dto.base_dto import BaseDTO


class EnergyTransactionResponseDTO(BaseDTO):
    """Representação de saída de uma transação de energia (inclui id/timestamps do `BaseDTO`)."""

    negotiation_id: UUID = Field(
        ...,
        description="Id da negociação à qual a transação pertence",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    amount: Decimal = Field(
        ...,
        description="Quantidade de energia negociada (em MWh)",
        examples=["1500.00"],
    )
    price: Decimal = Field(
        ...,
        description="Preço da transação",
        examples=["1500.00"],
    )
    type: TransactionType = Field(
        ...,
        description="Tipo da transação (BUY, SELL)",
        examples=["BUY"],
    )
    transaction_date: datetime = Field(
        ...,
        description="Data/hora da transação",
        examples=["2026-07-12T14:30:00Z"],
    )
