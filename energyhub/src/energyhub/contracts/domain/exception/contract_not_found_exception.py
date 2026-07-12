"""Exceção: contrato não encontrado."""

from __future__ import annotations

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class ContractNotFoundException(ResourceNotFoundException):
    """Lançada quando um contrato solicitado não existe (→ HTTP 404)."""
