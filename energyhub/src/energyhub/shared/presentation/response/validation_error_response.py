"""Modelo de resposta para erros de validação de requisição (um item por campo)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FieldError(BaseModel):
    """Falha de validação em um campo específico da requisição."""

    field: str = Field(
        ...,
        description="Nome do campo que falhou na validação (caminho ponto-separado).",
        examples=["email"],
    )
    message: str = Field(
        ...,
        description="Motivo legível da falha de validação do campo.",
        examples=["value is not a valid email address"],
    )


class ValidationErrorResponse(BaseModel):
    """Corpo retornado quando a validação de schema da requisição falha (HTTP 400)."""

    status: int = Field(
        default=400,
        description="Código de status HTTP (sempre 400 para erros de validação de entrada).",
        examples=[400],
    )
    message: str = Field(
        default="Erro de validação",
        description="Resumo do erro de validação.",
        examples=["Erro de validação"],
    )
    errors: list[FieldError] = Field(
        default_factory=list,
        description="Lista de erros — um `FieldError` por campo inválido.",
    )
