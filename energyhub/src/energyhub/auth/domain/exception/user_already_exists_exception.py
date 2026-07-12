"""Exceção: usuário já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class UserAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um usuário com username/e-mail já cadastrado (→ HTTP 409)."""
