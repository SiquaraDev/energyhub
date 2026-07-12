from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException
from energyhub.shared.util.date_utils import utcnow

if TYPE_CHECKING:
    from energyhub.auth.domain.entity.user import User


@dataclass(kw_only=True, eq=False)
class AuditLog(BaseEntity):
    """Registro de auditoria de uma ação realizada por um usuário sobre uma entidade."""

    user_id: UUID
    action: AuditAction
    entity_type: str
    entity_id: UUID
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=utcnow)
    user: User | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.entity_type or not self.entity_type.strip():
            raise ValidationException("entity_type não pode ser vazio")
