"""DTO de request de transação de energia."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from energyhub.negotiations.domain.entity.transaction_type import TransactionType


class EnergyTransactionRequestDTO(BaseModel):
    """Dados de entrada de uma transação de energia (sub-recurso da negociação).

    `negotiation_id` vem do path (`POST /negotiations/{negotiation_id}/transactions`), não do corpo.
    """

    amount: Decimal = Field(
        ...,
        gt=0,
        description="Quantidade de energia negociada (em MWh)",
        examples=["1500.00"],
    )
    price: Decimal = Field(
        ...,
        gt=0,
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
