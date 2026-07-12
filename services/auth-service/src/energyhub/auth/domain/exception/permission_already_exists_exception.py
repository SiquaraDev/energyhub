"""Exceção: permissão já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class PermissionAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar uma permissão com um nome já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "PERMISSION_ALREADY_EXISTS"
