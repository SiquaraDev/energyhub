"""DTO de request de papel (role)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_non_empty


class RoleRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um papel (com permissões por id)."""

    name: str = Field(..., description="Nome do papel (ex.: ADMIN)")
    description: str | None = Field(None, description="Descrição do papel")
    permission_ids: list[UUID] = Field(
        default_factory=list, description="IDs das permissões atribuídas ao papel"
    )

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_non_empty(value)
