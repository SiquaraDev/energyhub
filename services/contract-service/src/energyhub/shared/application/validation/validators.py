"""Validadores de entrada reutilizáveis (funções standalone, independentemente testáveis).

Aplicados aos DTOs de request via `@field_validator`. Levantam `ValueError` (que o Pydantic
converte em erro de validação identificando o campo).
"""

from __future__ import annotations

import re

from energyhub.shared.domain.valueobject.cnpj import CNPJ

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_cnpj(value: str) -> str:
    """Valida um CNPJ (14 dígitos + dígitos verificadores); retorna o valor inalterado.

    Reutiliza o algoritmo do _value object_ `CNPJ` (que aceita a forma formatada ou 14 dígitos).
    """
    CNPJ(value)  # levanta ValueError se o CNPJ for inválido
    return value


def validate_non_empty(value: str) -> str:
    """Rejeita string vazia ou só com espaços; retorna o valor inalterado."""
    if not value or not value.strip():
        raise ValueError("valor não pode ser vazio")
    return value


def validate_email(value: str) -> str:
    """Valida o formato de um e-mail; retorna o valor inalterado."""
    if not _EMAIL_RE.match(value):
        raise ValueError("e-mail inválido")
    return value
