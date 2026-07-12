"""Handler que traduz exceções de domínio em respostas HTTP padronizadas.

Registrado para a base `DomainException`, cobrindo todas as subclasses. O mapeamento por tipo:
- `ResourceNotFoundException` → 404
- `BusinessRuleException` → 409 (ex.: já-existe, estado inválido)
- `ValidationException` → 422
- demais `DomainException` → 422 (fallback seguro)
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from energyhub.shared.domain.exception.business_rule_exception import BusinessRuleException
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.domain.exception.resource_not_found_exception import (
    ResourceNotFoundException,
)
from energyhub.shared.domain.exception.validation_exception import ValidationException
from energyhub.shared.presentation.response.error_response import ErrorResponse

# Ordem importa: subclasses mais específicas primeiro.
_MAPPING: list[tuple[type[DomainException], int, str]] = [
    (ResourceNotFoundException, 404, "Not Found"),
    (BusinessRuleException, 409, "Conflict"),
    (ValidationException, 422, "Unprocessable Entity"),
]

_FALLBACK = (422, "Unprocessable Entity")


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Converte uma `DomainException` na resposta HTTP correspondente ao seu tipo."""
    status, error = _FALLBACK
    for exc_type, code, label in _MAPPING:
        if isinstance(exc, exc_type):
            status, error = code, label
            break

    body = ErrorResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        status=status,
        error=error,
        message=exc.message,
        path=request.url.path,
    )
    return JSONResponse(status_code=status, content=asdict(body))
