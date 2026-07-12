from __future__ import annotations

from enum import Enum


class NotificationStatus(str, Enum):
    """Estados do ciclo de vida de uma notificação."""

    PENDING = "PENDING"
    SENT = "SENT"
    READ = "READ"
    FAILED = "FAILED"
