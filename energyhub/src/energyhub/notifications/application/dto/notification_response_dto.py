"""DTO de resposta de notificação."""

from __future__ import annotations

from uuid import UUID

from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class NotificationResponseDTO(BaseDTO):
    """Representação de saída de uma notificação (inclui id/timestamps do `BaseDTO`)."""

    user_id: UUID
    title: str
    message: str
    status: NotificationStatus = NotificationStatus.PENDING
