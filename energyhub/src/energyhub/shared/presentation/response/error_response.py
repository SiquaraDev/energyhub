"""Modelo de resposta de erro padronizada da API (documentado no OpenAPI)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Corpo padronizado de erro retornado pela API em falhas `4xx`/`5xx`."""

    timestamp: str = Field(
        ...,
        description="Instante do erro em ISO-8601 (UTC).",
        examples=["2026-07-12T12:00:00+00:00"],
    )
    status: int = Field(
        ...,
        description="Código de status HTTP da resposta.",
        examples=[404],
    )
    error: str = Field(
        ...,
        description="Rótulo do tipo de erro (razão do status HTTP).",
        examples=["Not Found"],
    )
    message: str = Field(
        ...,
        description="Mensagem legível descrevendo a causa do erro.",
        examples=["Cliente 0b1e... não encontrado"],
    )
    path: str = Field(
        ...,
        description="Caminho da requisição que originou o erro.",
        examples=["/api/v1/clients/0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    error_code: str | None = Field(
        default=None,
        description=(
            "Código de erro estável e legível por máquina (ver `docs/API_ERRORS.md`); "
            "permite ao cliente ramificar sem depender da mensagem."
        ),
        examples=["CLIENT_NOT_FOUND"],
    )
