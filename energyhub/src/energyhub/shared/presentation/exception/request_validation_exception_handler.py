"""Handler para erros de validação de schema da requisição (Pydantic) → HTTP 400.

Sobrescreve o padrão do FastAPI (422) para `RequestValidationError`, devolvendo um
`ValidationErrorResponse` com um `FieldError` por campo inválido, alinhado ao schema documentado.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from energyhub.shared.presentation.response.validation_error_response import (
    FieldError,
    ValidationErrorResponse,
)

# Prefixos de localização do Pydantic que não fazem parte do nome do campo em si.
_LOCATION_PREFIXES = {"body", "query", "path", "header", "cookie"}


def _field_name(location: tuple[object, ...]) -> str:
    """Converte o `loc` do Pydantic em um nome de campo legível (sem o prefixo de origem)."""
    parts = list(location)
    if parts and parts[0] in _LOCATION_PREFIXES:
        parts = parts[1:]
    return ".".join(str(part) for part in parts) or "body"


async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Traduz falhas de validação de entrada em 400 com a lista de campos inválidos."""
    errors = [
        FieldError(field=_field_name(error["loc"]), message=error["msg"]) for error in exc.errors()
    ]
    body = ValidationErrorResponse(status=400, message="Erro de validação", errors=errors)
    return JSONResponse(status_code=400, content=body.model_dump())
