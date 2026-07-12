from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.clients.domain.entity.client import Client


@dataclass(kw_only=True, eq=False)
class Invoice(BaseEntity):
    """Fatura emitida a um cliente (raiz do FinancialAggregate)."""

    invoice_number: str
    client_id: UUID
    amount: Decimal
    due_date: date
    status: InvoiceStatus = InvoiceStatus.DRAFT
    client: Client | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.invoice_number or not self.invoice_number.strip():
            raise ValidationException("invoice_number não pode ser vazio")
        if self.amount < Decimal("0"):
            raise ValidationException("amount não pode ser negativo")
