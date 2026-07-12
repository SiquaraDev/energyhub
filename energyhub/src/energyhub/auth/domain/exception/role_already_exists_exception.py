"""Exceção: papel já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class RoleAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um papel com um nome já cadastrado (→ HTTP 409)."""
