"""DTO de request de log de auditoria."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.shared.application.validation.validators import validate_non_empty


class AuditLogRequestDTO(BaseModel):
    """Dados de entrada para registrar um log de auditoria (recurso append-only)."""

    user_id: UUID = Field(
        ...,
        description="Id do usuário que realizou a ação",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    action: AuditAction = Field(..., description="Ação auditável realizada", examples=["CREATE"])
    entity_type: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Tipo da entidade afetada",
        examples=["Client"],
    )
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

    @field_validator("entity_type")
    @classmethod
    def _validate_entity_type(cls, value: str) -> str:
        return validate_non_empty(value)
