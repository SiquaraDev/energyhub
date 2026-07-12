"""Utilitários genéricos de validação (validações ricas ficam nos Value Objects)."""

import re

from energyhub.shared.util.string_utils import only_digits

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    """Validação básica de formato de e-mail."""
    return bool(_EMAIL_RE.match(value))


def is_valid_cnpj_length(value: str) -> bool:
    """Verifica se o CNPJ tem 14 dígitos (validação de DV vive no VO CNPJ, Fase 3)."""
    return len(only_digits(value)) == 14


def is_positive(value: float) -> bool:
    """Indica se o número é estritamente positivo."""
    return value > 0
