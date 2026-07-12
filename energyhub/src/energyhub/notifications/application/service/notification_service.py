"""Serviço de aplicação do agregado `Notification` (regras sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from energyhub.notifications.application.dto.notification_request_dto import (
    NotificationRequestDTO,
)
from energyhub.notifications.application.dto.notification_response_dto import (
    NotificationResponseDTO,
)
from energyhub.notifications.application.mapper.notification_mapper import NotificationMapper
from energyhub.notifications.domain.exception.notification_not_found_exception import (
    NotificationNotFoundException,
)
from energyhub.notifications.infrastructure.persistence.notification_repository import (
    NotificationRepository,
)
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class NotificationService:
    """CRUD de notificações. Faz `flush` via repositório; o `commit` fica com a sessão
    por requisição (`get_session`)."""

    def __init__(
        self,
        repository: NotificationRepository,
        mapper: NotificationMapper | None = None,
    ) -> None:
        self._repository = repository
        self._mapper = mapper or NotificationMapper()

    async def create(self, dto: NotificationRequestDTO) -> NotificationResponseDTO:
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, notification_id: UUID) -> NotificationResponseDTO:
        entity = await self._repository.find_by_id(notification_id)
        if entity is None:
            raise NotificationNotFoundException(f"Notificação {notification_id} não encontrada")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[NotificationResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(
        self, notification_id: UUID, dto: NotificationRequestDTO
    ) -> NotificationResponseDTO:
        entity = await self._repository.find_by_id(notification_id)
        if entity is None:
            raise NotificationNotFoundException(f"Notificação {notification_id} não encontrada")
        entity.title = dto.title
        entity.message = dto.message
        entity.status = dto.status
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def delete(self, notification_id: UUID) -> None:
        if not await self._repository.exists_by_id(notification_id):
            raise NotificationNotFoundException(f"Notificação {notification_id} não encontrada")
        await self._repository.delete_by_id(notification_id)
