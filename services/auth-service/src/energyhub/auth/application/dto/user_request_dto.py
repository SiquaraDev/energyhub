"""DTO de request de usuário."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_email, validate_non_empty


class UserRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um usuário (senha em texto puro; papéis por id)."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nome de usuário (único)",
        examples=["operador01"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,
        description="Senha em texto puro (será hasheada antes de persistir)",
        examples=["SenhaForte123!"],
    )
    email: str = Field(
        ...,
        min_length=3,
        max_length=254,
        description="E-mail (único)",
        examples=["usuario@energyhub.example"],
    )
    full_name: str | None = Field(
        None,
        max_length=255,
        description="Nome completo",
        examples=["Operador da Silva"],
    )
    active: bool = Field(
        True,
        description="Indica se o usuário está ativo",
        examples=[True],
    )
    role_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs dos papéis atribuídos ao usuário",
        examples=[["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"]],
    )

    @field_validator("username")
    @classmethod
    def _validate_username(cls, value: str) -> str:
        return validate_non_empty(value)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        return validate_email(value)
