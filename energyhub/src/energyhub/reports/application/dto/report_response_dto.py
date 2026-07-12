"""DTO de resposta de relatório."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from energyhub.shared.application.dto.base_dto import BaseDTO


class ReportResponseDTO(BaseDTO):
    """Representação de saída de um relatório (inclui id/timestamps do `BaseDTO`)."""

    report_type: str = Field(..., description="Tipo do relatório", examples=["CONSUMPTION_MONTHLY"])
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
        examples=["/reports/2026/07/report-0b1e5b2e.pdf"],
    )
    status: str = Field(
        "PENDING",
        description="Status atual do relatório (ex.: PENDING, PROCESSING, DONE)",
        examples=["PENDING"],
    )
