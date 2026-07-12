from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Valor monetário com moeda associada (imutável)."""

    amount: Decimal
    currency: str = "BRL"
