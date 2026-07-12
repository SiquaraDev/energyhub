"""Exceção: usuário já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class UserAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um usuário com username/e-mail já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "USER_ALREADY_EXISTS"
