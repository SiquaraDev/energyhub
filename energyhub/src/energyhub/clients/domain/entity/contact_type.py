from __future__ import annotations

from enum import Enum


class ContactType(str, Enum):
    """Tipos de contato associados a um cliente."""

    PRIMARY = "PRIMARY"
    BILLING = "BILLING"
    TECHNICAL = "TECHNICAL"
    COMMERCIAL = "COMMERCIAL"
