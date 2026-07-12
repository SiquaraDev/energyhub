"""DTO de resposta de transação de energia."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.shared.application.dto.base_dto import BaseDTO


class EnergyTransactionResponseDTO(BaseDTO):
    """Representação de saída de uma transação de energia (inclui id/timestamps do `BaseDTO`)."""

    negotiation_id: UUID
    amount: Decimal
    price: Decimal
    type: TransactionType
    transaction_date: datetime
