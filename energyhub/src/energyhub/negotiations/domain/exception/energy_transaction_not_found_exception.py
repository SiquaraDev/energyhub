"""Exceção: transação de energia não encontrada."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class EnergyTransactionNotFoundException(ResourceNotFoundException):
    """Lançada quando uma transação de energia solicitada não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "ENERGY_TRANSACTION_NOT_FOUND"
