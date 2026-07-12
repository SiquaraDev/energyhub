"""DTO de request de relatório."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.shared.application.validation.validators import validate_non_empty


class ReportRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um relatório."""

    report_type: str = Field(
        ...,
        description="Tipo do relatório",
        min_length=1,
        max_length=100,
        examples=["CONSUMPTION_MONTHLY"],
    )
    generated_by: UUID = Field(
        ...,
        description="Id do usuário que gerou o relatório",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parâmetros de geração do relatório (JSONB)",
        examples=[{"month": "2026-07", "client_id": "0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"}],
    )
    file_path: str | None = Field(
        None,
        description="Caminho do arquivo gerado",
        max_length=1024,
        examples=["/reports/2026/07/report-0b1e5b2e.pdf"],
    )

    @field_validator("report_type")
    @classmethod
    def _validate_report_type(cls, value: str) -> str:
        return validate_non_empty(value)
