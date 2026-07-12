"""Mapper entre entidades de `notifications` e seus DTOs."""

from __future__ import annotations

from energyhub.notifications.application.dto.notification_request_dto import (
    NotificationRequestDTO,
)
from energyhub.notifications.application.dto.notification_response_dto import (
    NotificationResponseDTO,
)
from energyhub.notifications.domain.entity.notification import Notification


class NotificationMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Notification`."""

    @staticmethod
    def to_entity(dto: NotificationRequestDTO) -> Notification:
        """Constrói uma `Notification` a partir do request DTO (id/timestamps na persistência)."""
        return Notification(
            user_id=dto.user_id,
            title=dto.title,
            message=dto.message,
            status=dto.status,
        )

    @staticmethod
    def to_response_dto(entity: Notification) -> NotificationResponseDTO:
        """Constrói o response DTO da entidade via from_attributes."""
        return NotificationResponseDTO.model_validate(entity)
