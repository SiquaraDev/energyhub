from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumber:
    """Número de telefone validado e normalizado (imutável).

    Mantém apenas os dígitos, aceitando de 10 a 13 caracteres
    (incluindo DDD e eventual código de país).
    """

    value: str

    def __post_init__(self) -> None:
        digits = "".join(c for c in self.value if c.isdigit())
        if not 10 <= len(digits) <= 13:
            raise ValueError(f"Número de telefone inválido: {self.value!r}")
        object.__setattr__(self, "value", digits)
