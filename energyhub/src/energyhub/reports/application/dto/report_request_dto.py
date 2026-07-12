"""DTO de request de relatório."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_non_empty


class ReportRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um relatório."""

    report_type: str = Field(..., description="Tipo do relatório")
    generated_by: UUID = Field(..., description="Id do usuário que gerou o relatório")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parâmetros de geração do relatório (JSONB)"
    )
    file_path: str | None = Field(None, description="Caminho do arquivo gerado")

    @field_validator("report_type")
    @classmethod
    def _validate_report_type(cls, value: str) -> str:
        return validate_non_empty(value)
