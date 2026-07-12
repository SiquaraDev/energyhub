"""Exceção: cliente já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class ClientAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um cliente com um CNPJ já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "CLIENT_ALREADY_EXISTS"
