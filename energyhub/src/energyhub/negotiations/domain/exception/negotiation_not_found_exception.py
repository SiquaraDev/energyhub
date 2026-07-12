"""Exceção: negociação não encontrada."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class NegotiationNotFoundException(ResourceNotFoundException):
    """Lançada quando uma negociação solicitada não existe (→ HTTP 404)."""
