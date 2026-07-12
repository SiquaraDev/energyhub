"""DTO de request de log de auditoria."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.shared.application.validation.validators import validate_non_empty


class AuditLogRequestDTO(BaseModel):
    """Dados de entrada para registrar um log de auditoria (recurso append-only)."""

    user_id: UUID = Field(..., description="Id do usuário que realizou a ação")
    action: AuditAction = Field(..., description="Ação auditável realizada")
    entity_type: str = Field(..., description="Tipo da entidade afetada")
    entity_id: UUID = Field(..., description="Id da entidade afetada")
    details: dict[str, Any] = Field(
        default_factory=dict, description="Detalhes adicionais da ação (JSONB)"
    )

    @field_validator("entity_type")
    @classmethod
    def _validate_entity_type(cls, value: str) -> str:
        return validate_non_empty(value)
