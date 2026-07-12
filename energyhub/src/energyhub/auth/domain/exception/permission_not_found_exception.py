"""Exceção: permissão não encontrada."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class PermissionNotFoundException(ResourceNotFoundException):
    """Lançada quando uma permissão solicitada não existe (→ HTTP 404)."""
