"""DTO de resposta de relatório."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import Field

from energyhub.shared.application.dto.base_dto import BaseDTO


class ReportResponseDTO(BaseDTO):
    """Representação de saída de um relatório (inclui id/timestamps do `BaseDTO`)."""

    report_type: str
    generated_by: UUID
    parameters: dict[str, Any] = Field(default_factory=dict)
    file_path: str | None = None
    status: str = "PENDING"
