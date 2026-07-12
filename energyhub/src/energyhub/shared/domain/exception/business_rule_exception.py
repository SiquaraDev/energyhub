"""Exceção de violação de regra de negócio."""

from typing import ClassVar

from energyhub.shared.domain.exception.domain_exception import DomainException


class BusinessRuleException(DomainException):
    """Lançada quando uma regra de negócio é violada."""

    error_code: ClassVar[str] = "BUSINESS_RULE_VIOLATION"
