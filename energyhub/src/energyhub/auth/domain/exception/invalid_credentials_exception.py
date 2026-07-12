"""Exceção: credenciais inválidas (usada no fluxo de login da Fase 7)."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.validation_exception import ValidationException


class InvalidCredentialsException(ValidationException):
    """Lançada quando as credenciais de autenticação são inválidas."""

    error_code: ClassVar[str] = "INVALID_CREDENTIALS"
