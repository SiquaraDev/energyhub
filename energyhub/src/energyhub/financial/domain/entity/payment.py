from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.financial.domain.entity.invoice import Invoice


@dataclass(kw_only=True, eq=False)
class Payment(BaseEntity):
    """Pagamento associado a uma fatura."""

    invoice_id: UUID
    amount: Decimal
    payment_date: datetime
    invoice: Invoice | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.amount <= Decimal("0"):
            raise ValidationException("amount deve ser positivo")
