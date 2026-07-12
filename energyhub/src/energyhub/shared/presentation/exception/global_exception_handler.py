"""Handler global de exceções não tratadas da aplicação."""

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from energyhub.shared.presentation.response.error_response import ErrorResponse


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Converte qualquer exceção não tratada numa resposta 500 padronizada."""
    error = ErrorResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        status=500,
        error="Internal Server Error",
        message=str(exc),
        path=request.url.path,
    )
    return JSONResponse(status_code=500, content=asdict(error))
