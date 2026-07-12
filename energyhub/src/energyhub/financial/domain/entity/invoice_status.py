from __future__ import annotations

from enum import Enum


class InvoiceStatus(str, Enum):
    """Estados do ciclo de vida de uma fatura."""

    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
