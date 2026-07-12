"""Exceção: fatura já existente."""

from __future__ import annotations

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException


class InvoiceAlreadyExistsException(BusinessRuleException):
    """Lançada ao criar uma fatura com um número já cadastrado (→ HTTP 409)."""
