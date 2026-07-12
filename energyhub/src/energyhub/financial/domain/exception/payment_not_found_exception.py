"""Exceção: pagamento não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class PaymentNotFoundException(ResourceNotFoundException):
    """Lançada quando um pagamento solicitado não existe (→ HTTP 404)."""
