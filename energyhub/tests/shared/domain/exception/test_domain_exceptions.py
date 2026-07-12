"""Testes unitários da hierarquia de exceções de domínio (mensagem + error_code)."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.domain.exception.message_publishing_exception import (
    MessagePublishingException,
)
from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from energyhub.shared.domain.exception.validation_exception import ValidationException


def test_domain_exception_carries_message_and_default_code() -> None:
    exc = DomainException("algo deu errado")
    assert exc.message == "algo deu errado"
    assert str(exc) == "algo deu errado"
    assert exc.error_code == "DOMAIN_ERROR"


def test_subclasses_expose_their_error_codes() -> None:
    assert ResourceNotFoundException("x").error_code == "RESOURCE_NOT_FOUND"
    assert BusinessRuleException("x").error_code == "BUSINESS_RULE_VIOLATION"
    assert ValidationException("x").error_code == "VALIDATION_ERROR"
    assert MessagePublishingException("x").error_code == "MESSAGE_PUBLISHING_ERROR"


def test_subclasses_are_domain_exceptions() -> None:
    assert isinstance(ResourceNotFoundException("x"), DomainException)
    assert isinstance(BusinessRuleException("x"), DomainException)
    assert isinstance(ValidationException("x"), DomainException)
