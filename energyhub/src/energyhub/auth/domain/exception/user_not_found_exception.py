"""Exceção: usuário não encontrado."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)


class UserNotFoundException(ResourceNotFoundException):
    """Lançada quando um usuário solicitado não existe (→ HTTP 404)."""

    error_code: ClassVar[str] = "USER_NOT_FOUND"
