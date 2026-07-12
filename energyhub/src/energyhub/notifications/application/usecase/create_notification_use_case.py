"""Caso de uso: criar notificação."""

from __future__ import annotations

from energyhub.notifications.application.dto.notification_request_dto import (
    NotificationRequestDTO,
)
from energyhub.notifications.application.dto.notification_response_dto import (
    NotificationResponseDTO,
)
from energyhub.notifications.application.service.notification_service import NotificationService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateNotificationUseCase(UseCase[NotificationRequestDTO, NotificationResponseDTO]):
    """Orquestra a criação de uma notificação delegando ao `NotificationService`."""

    def __init__(self, service: NotificationService) -> None:
        self._service = service

    async def execute(self, input_data: NotificationRequestDTO) -> NotificationResponseDTO:
        return await self._service.create(input_data)
