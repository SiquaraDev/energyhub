"""Exceção de recurso não encontrado."""

from energyhub.shared.domain.exception.domain_exception import DomainException


class ResourceNotFoundException(DomainException):
    """Lançada quando um recurso solicitado não existe."""
