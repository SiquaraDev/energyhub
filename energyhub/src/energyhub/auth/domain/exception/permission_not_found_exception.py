"""Exceção: permissão não encontrada."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class PermissionNotFoundException(ResourceNotFoundException):
    """Lançada quando uma permissão solicitada não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "PERMISSION_NOT_FOUND"
