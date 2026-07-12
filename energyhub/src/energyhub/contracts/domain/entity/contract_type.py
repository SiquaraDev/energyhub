from __future__ import annotations

from enum import Enum


class ContractType(str, Enum):
    """Tipos de contrato de energia."""

    PURCHASE = "PURCHASE"
    SALE = "SALE"
    BIDIRECTIONAL = "BIDIRECTIONAL"
