from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """Endereço postal (imutável)."""

    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"
