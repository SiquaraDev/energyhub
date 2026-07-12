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

    user_id: UUID
    action: AuditAction
    entity_type: str
    entity_id: UUID
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
