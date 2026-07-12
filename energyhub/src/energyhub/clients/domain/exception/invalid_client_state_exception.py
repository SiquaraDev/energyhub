from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.domain_exception import DomainException


class InvalidClientStateException(DomainException):
    """Estado ou transição inválida para o cliente."""

    error_code: ClassVar[str] = "INVALID_CLIENT_STATE"
