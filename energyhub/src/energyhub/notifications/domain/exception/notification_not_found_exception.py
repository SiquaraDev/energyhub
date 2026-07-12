"""Exceção: notificação não encontrada."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class NotificationNotFoundException(ResourceNotFoundException):
    """Lançada quando uma notificação solicitada não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "NOTIFICATION_NOT_FOUND"
