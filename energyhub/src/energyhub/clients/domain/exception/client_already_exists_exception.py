"""Exceção: cliente já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class ClientAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um cliente com um CNPJ já cadastrado (→ HTTP 409)."""
