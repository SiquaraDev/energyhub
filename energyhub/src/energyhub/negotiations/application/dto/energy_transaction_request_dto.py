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

    amount: Decimal = Field(..., description="Quantidade de energia negociada")
    price: Decimal = Field(..., description="Preço da transação")
    type: TransactionType = Field(..., description="Tipo da transação (BUY, SELL)")
    transaction_date: datetime = Field(..., description="Data/hora da transação")
