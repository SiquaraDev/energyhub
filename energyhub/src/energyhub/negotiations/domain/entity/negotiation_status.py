from __future__ import annotations

from enum import Enum


class NegotiationStatus(str, Enum):
    """Estados do ciclo de vida de uma negociação."""

    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
