"""Exceção: permissão já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class PermissionAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar uma permissão com um nome já cadastrado (→ HTTP 409)."""
