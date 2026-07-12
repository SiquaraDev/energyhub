"""Exceção: contrato já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class ContractAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar um contrato com um número já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "CONTRACT_ALREADY_EXISTS"
