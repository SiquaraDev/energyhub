from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.shared.domain.entity.base_entity import BaseEntity

if TYPE_CHECKING:
    from energyhub.negotiations.domain.entity.negotiation import Negotiation


@dataclass(kw_only=True)
class EnergyTransaction(BaseEntity):
    """Transação de energia (compra/venda) pertencente a uma negociação."""

    negotiation_id: UUID
    amount: Decimal
    price: Decimal
    type: TransactionType
    transaction_date: datetime
    negotiation: Negotiation | None = field(default=None, compare=False, repr=False)
