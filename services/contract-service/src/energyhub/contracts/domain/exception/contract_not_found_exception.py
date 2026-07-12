"""Exceção: contrato não encontrado."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class ContractNotFoundException(ResourceNotFoundException):
    """Lançada quando um contrato solicitado não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "CONTRACT_NOT_FOUND"
