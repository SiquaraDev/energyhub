"""Exceção: fatura já existente."""

from __future__ import annotations

from typing import ClassVar

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class InvoiceAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar uma fatura com um número já cadastrado (→ HTTP 409)."""

    error_code: ClassVar[str] = "INVOICE_ALREADY_EXISTS"
