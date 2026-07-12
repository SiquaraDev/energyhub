"""Exceção: contrato já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class ContractAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um contrato com um número já cadastrado (→ HTTP 409)."""
