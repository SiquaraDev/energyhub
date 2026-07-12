"""Exceção: cliente não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class ClientNotFoundException(ResourceNotFoundException):
    """Lançada quando um cliente solicitado não existe (→ HTTP 404)."""
