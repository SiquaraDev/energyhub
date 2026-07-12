"""Exceção de recurso não encontrado."""

from typing import ClassVar

from energyhub.shared.domain.exception.domain_exception import DomainException


class ResourceNotFoundException(DomainException):
    """Lançada quando um recurso solicitado não existe."""

    error_code: ClassVar[str] = "RESOURCE_NOT_FOUND"
