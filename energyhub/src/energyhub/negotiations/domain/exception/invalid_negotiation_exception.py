from __future__ import annotations

from energyhub.shared.domain.exception.domain_exception import DomainException


class InvalidNegotiationException(DomainException):
    """Operação ou estado inválido para a negociação."""
