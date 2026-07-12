"""Contrato de mensagem do evento de auditoria (Fase 10).

`AuditEvent` é o **contrato tipado** das mensagens publicadas na fila de auditoria: o produtor
serializa este modelo e o `AuditConsumer` reconstrói um `AuditLog` a partir dos seus campos.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from energyhub.shared.util.date_utils import utcnow


class AuditEvent(BaseModel):
    """Evento de auditoria: quem (`user_id`) fez o quê (`action`) sobre qual entidade."""

    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utcnow)
