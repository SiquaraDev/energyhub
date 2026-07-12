"""DTO de request de papel (role)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_non_empty


class RoleRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um papel (com permissões por id)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome do papel (ex.: ADMIN)",
        examples=["ADMIN"],
    )
    description: str | None = Field(
        None,
        max_length=255,
        description="Descrição do papel",
        examples=["Administrador do sistema"],
    )
    permission_ids: list[UUID] = Field(
        default_factory=list,
        description="IDs das permissões atribuídas ao papel",
        examples=[["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"]],
    )

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_non_empty(value)
