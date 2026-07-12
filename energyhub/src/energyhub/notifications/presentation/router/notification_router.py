"""Router REST do módulo `notifications` (CRUD + listagem paginada)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.notifications.application.dto.notification_request_dto import (
    NotificationRequestDTO,
)
from energyhub.notifications.application.dto.notification_response_dto import (
    NotificationResponseDTO,
)
from energyhub.notifications.application.service.notification_service import NotificationService
from energyhub.notifications.application.usecase.create_notification_use_case import (
    CreateNotificationUseCase,
)
from energyhub.notifications.infrastructure.persistence.notification_repository import (
    NotificationRepository,
)
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_notification_service(
    session: AsyncSession = Depends(get_session),
) -> NotificationService:
    """Provedor do `NotificationService` por requisição (repositório sobre a sessão)."""
    return NotificationService(NotificationRepository(session))


def get_create_notification_use_case(
    service: NotificationService = Depends(get_notification_service),
) -> CreateNotificationUseCase:
    """Provedor do caso de uso de criação de notificação."""
    return CreateNotificationUseCase(service)


class NotificationRouter(BaseRouter):
    """Registra os endpoints REST de notificações sob `/api/v1/notifications`."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/notifications", tags=["notifications"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=NotificationResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria uma notificação",
        )
        async def create(
            dto: NotificationRequestDTO,
            use_case: CreateNotificationUseCase = Depends(get_create_notification_use_case),
        ) -> NotificationResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{notification_id}",
            response_model=NotificationResponseDTO,
            summary="Busca uma notificação por id",
        )
        async def find_by_id(
            notification_id: UUID,
            service: NotificationService = Depends(get_notification_service),
        ) -> NotificationResponseDTO:
            return await service.find_by_id(notification_id)

        @router.get(
            "",
            response_model=PageResponse[NotificationResponseDTO],
            summary="Lista notificações (paginado)",
        )
        async def find_all(
            service: NotificationService = Depends(get_notification_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[NotificationResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{notification_id}",
            response_model=NotificationResponseDTO,
            summary="Atualiza uma notificação",
        )
        async def update(
            notification_id: UUID,
            dto: NotificationRequestDTO,
            service: NotificationService = Depends(get_notification_service),
        ) -> NotificationResponseDTO:
            return await service.update(notification_id, dto)

        @router.delete(
            "/{notification_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove uma notificação",
        )
        async def delete(
            notification_id: UUID,
            service: NotificationService = Depends(get_notification_service),
        ) -> None:
            await service.delete(notification_id)
