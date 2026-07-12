from __future__ import annotations

from energyhub.shared.domain.exception.domain_exception import DomainException


class InvalidClientStateException(DomainException):
    """Estado ou transição inválida para o cliente."""
