"""DTO de resposta de log de auditoria."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.shared.application.dto.base_dto import BaseDTO


class AuditLogResponseDTO(BaseDTO):
    """Representação de saída de um log de auditoria (inclui id/timestamps do `BaseDTO`)."""

    user_id: UUID = Field(
        ...,
        description="Id do usuário que realizou a ação",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    action: AuditAction = Field(..., description="Ação auditável realizada", examples=["CREATE"])
    entity_type: str = Field(..., description="Tipo da entidade afetada", examples=["Client"])
    entity_id: UUID = Field(
        ...,
        description="Id da entidade afetada",
        examples=["1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c5d"],
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Detalhes adicionais da ação (JSONB)",
        examples=[{"ip": "203.0.113.10", "field": "status"}],
    )
    timestamp: datetime = Field(
        ...,
        description="Momento em que a ação foi registrada",
        examples=["2026-07-12T14:30:00Z"],
    )
