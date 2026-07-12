"""Exceção: fatura não encontrada."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class InvoiceNotFoundException(ResourceNotFoundException):
    """Lançada quando uma fatura solicitada não existe (→ HTTP 404)."""
