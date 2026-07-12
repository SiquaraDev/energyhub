"""Blocos reutilizáveis de `responses` do OpenAPI para documentar erros por status.

Os routers compõem estes dicionários no argumento `responses` de cada rota, garantindo que os
corpos de erro documentados apontem para os mesmos modelos (`ErrorResponse` /
`ValidationErrorResponse`) que os handlers globais emitem em runtime. Ex.:

    responses={**BAD_REQUEST, **CONFLICT, **UNAUTHORIZED, **FORBIDDEN}
"""

from __future__ import annotations

from typing import Any

from energyhub.shared.presentation.response.error_response import ErrorResponse
from energyhub.shared.presentation.response.validation_error_response import (
    ValidationErrorResponse,
)

# 400 — validação de schema da requisição (um item por campo inválido).
BAD_REQUEST: dict[int | str, dict[str, Any]] = {
    400: {"model": ValidationErrorResponse, "description": "Erro de validação da requisição"}
}
# 401 — token ausente/inválido.
UNAUTHORIZED: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorResponse, "description": "Não autenticado (token ausente ou inválido)"}
}
# 403 — autenticado, porém sem a permissão exigida.
FORBIDDEN: dict[int | str, dict[str, Any]] = {
    403: {"model": ErrorResponse, "description": "Permissão insuficiente"}
}
# 404 — recurso não encontrado.
NOT_FOUND: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Recurso não encontrado"}
}
# 409 — conflito (já existe / regra de negócio / estado inválido).
CONFLICT: dict[int | str, dict[str, Any]] = {
    409: {"model": ErrorResponse, "description": "Conflito (recurso já existe ou estado inválido)"}
}
# 422 — violação de validação de domínio.
UNPROCESSABLE: dict[int | str, dict[str, Any]] = {
    422: {"model": ErrorResponse, "description": "Violação de validação de domínio"}
}

# Conjunto padrão para toda rota protegida (exige token + permissão).
AUTH_ERRORS: dict[int | str, dict[str, Any]] = {**UNAUTHORIZED, **FORBIDDEN}
