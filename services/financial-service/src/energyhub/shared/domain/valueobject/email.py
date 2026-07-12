from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """E-mail validado e normalizado (imutável)."""

    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError(f"E-mail inválido: {self.value!r}")
        object.__setattr__(self, "value", self.value.lower())
