from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Percentage:
    """Percentual validado entre 0 e 100 (imutável)."""

    value: Decimal

    def __post_init__(self) -> None:
        if not Decimal(0) <= self.value <= Decimal(100):
            raise ValueError(f"Percentual inválido (deve estar entre 0 e 100): {self.value!r}")
