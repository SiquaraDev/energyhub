"""Exceção: negociação não encontrada."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class NegotiationNotFoundException(ResourceNotFoundException):
    """Lançada quando uma negociação solicitada não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "NEGOTIATION_NOT_FOUND"
