"""DTO de request de permissão."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_non_empty


class PermissionRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar uma permissão."""

    name: str = Field(..., description="Nome da permissão (ex.: USER_CREATE)")
    description: str | None = Field(None, description="Descrição da permissão")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return validate_non_empty(value)
