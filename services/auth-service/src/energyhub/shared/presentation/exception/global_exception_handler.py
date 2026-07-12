"""Handler global de exceções não tratadas da aplicação (500 padronizado)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from energyhub.shared.presentation.response.error_response import ErrorResponse


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Converte qualquer exceção não tratada numa resposta 500 padronizada (`ErrorResponse`)."""
    body = ErrorResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        status=500,
        error="Internal Server Error",
        message="Ocorreu um erro interno inesperado.",
        path=request.url.path,
        error_code="INTERNAL_SERVER_ERROR",
    )
    return JSONResponse(status_code=500, content=body.model_dump())
