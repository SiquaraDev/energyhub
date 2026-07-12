"""Exceção de validação de domínio."""

from typing import ClassVar

from energyhub.shared.domain.exception.domain_exception import DomainException


class ValidationException(DomainException):
    """Lançada quando dados de entrada violam regras de validação do domínio."""

    error_code: ClassVar[str] = "VALIDATION_ERROR"
