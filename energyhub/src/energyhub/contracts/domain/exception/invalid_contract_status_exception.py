from __future__ import annotations

from energyhub.shared.domain.exception.domain_exception import DomainException


class InvalidContractStatusException(DomainException):
    """Transição de estado inválida para o contrato."""
