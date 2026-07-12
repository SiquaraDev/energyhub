"""Exceção: papel já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class RoleAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um papel com um nome já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "ROLE_ALREADY_EXISTS"
