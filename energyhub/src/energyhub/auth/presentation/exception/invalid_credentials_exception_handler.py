"""Handler que traduz `InvalidCredentialsException` em HTTP 401.

`InvalidCredentialsException` é subclasse de `ValidationException` (→ 422 no handler genérico de
domínio). Para o fluxo de autenticação, porém, a resposta correta é **401 Unauthorized** com o
cabeçalho `WWW-Authenticate: Bearer`. Como o Starlette despacha para o handler do tipo mais
específico na MRO da exceção, registrar este handler garante 401 no login sem afetar os demais
`ValidationException` (que continuam 422).
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.shared.presentation.response.error_response import ErrorResponse


async def invalid_credentials_exception_handler(
    request: Request, exc: InvalidCredentialsException
) -> JSONResponse:
    """Converte credenciais inválidas em 401 com `WWW-Authenticate: Bearer`."""
    body = ErrorResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        status=401,
        error="Unauthorized",
        message=exc.message,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=401,
        content=asdict(body),
        headers={"WWW-Authenticate": "Bearer"},
    )
