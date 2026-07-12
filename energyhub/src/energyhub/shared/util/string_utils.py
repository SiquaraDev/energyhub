"""Utilitários de manipulação de strings."""

import re

_WHITESPACE_RE = re.compile(r"\s+")


def is_blank(value: str | None) -> bool:
    """True se o valor for None ou composto apenas por espaços."""
    return value is None or value.strip() == ""


def normalize_whitespace(value: str) -> str:
    """Colapsa espaços internos e remove espaços das pontas."""
    return _WHITESPACE_RE.sub(" ", value).strip()


def only_digits(value: str) -> str:
    """Mantém apenas os dígitos da string (útil para CNPJ, telefone, etc.)."""
    return "".join(ch for ch in value if ch.isdigit())
