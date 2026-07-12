"""Exceção: CNPJ inválido."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.validation_exception import ValidationException


class InvalidCnpjException(ValidationException):
    """Lançada quando um CNPJ é inválido (→ HTTP 422)."""

    error_code: ClassVar[str] = "INVALID_CNPJ"
