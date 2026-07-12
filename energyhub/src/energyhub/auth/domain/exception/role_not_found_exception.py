"""Exceção: papel não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class RoleNotFoundException(ResourceNotFoundException):
    """Lançada quando um papel solicitado não existe (→ HTTP 404)."""
