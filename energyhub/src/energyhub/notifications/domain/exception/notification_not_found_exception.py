"""Exceção: notificação não encontrada."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class NotificationNotFoundException(ResourceNotFoundException):
    """Lançada quando uma notificação solicitada não existe (→ HTTP 404)."""
