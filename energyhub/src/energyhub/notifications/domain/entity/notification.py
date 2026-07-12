from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.auth.domain.entity.user import User


@dataclass(kw_only=True)
class Notification(BaseEntity):
    """Notificação destinada a um usuário do sistema."""

    user_id: UUID
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.PENDING
    user: User | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.title or not self.title.strip():
            raise ValidationException("title não pode ser vazio")
        if not self.message or not self.message.strip():
            raise ValidationException("message não pode ser vazio")
