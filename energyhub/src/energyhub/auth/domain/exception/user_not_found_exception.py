"""Exceção: usuário não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class UserNotFoundException(ResourceNotFoundException):
    """Lançada quando um usuário solicitado não existe (→ HTTP 404)."""
