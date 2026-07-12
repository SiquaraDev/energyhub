"""DTO de request de usuário."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_email, validate_non_empty


class UserRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um usuário (senha em texto puro; papéis por id)."""

    username: str = Field(..., min_length=1, description="Nome de usuário (único)")
    password: str = Field(..., min_length=6, max_length=72, description="Senha em texto puro")
    email: str = Field(..., description="E-mail (único)")
    full_name: str | None = Field(None, description="Nome completo")
    active: bool = Field(True, description="Indica se o usuário está ativo")
    role_ids: list[UUID] = Field(
        default_factory=list, description="IDs dos papéis atribuídos ao usuário"
    )

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return validate_email(value)
