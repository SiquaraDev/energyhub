"""Router REST de permissões (`/api/v1/permissions`)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.application.dto.permission_request_dto import PermissionRequestDTO
from energyhub.auth.application.dto.permission_response_dto import PermissionResponseDTO
from energyhub.auth.application.service.permission_service import PermissionService
from energyhub.auth.infrastructure.persistence.permission_repository import PermissionRepository
from energyhub.auth.infrastructure.persistence.role_repository import RoleRepository
from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.constant.permissions import (
    PERMISSION_CREATE,
    PERMISSION_DELETE,
    PERMISSION_READ,
    PERMISSION_UPDATE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_permission_service(session: AsyncSession = Depends(get_session)) -> PermissionService:
    """Provedor do `PermissionService` (com RoleRepository p/ `find_by_role_name`)."""
    return PermissionService(PermissionRepository(session), role_repository=RoleRepository(session))


class PermissionRouter(BaseRouter):
    """Endpoints REST de permissões."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/permissions",
            tags=["auth"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=PermissionResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria uma permissão",
            dependencies=[Depends(require_permission(PERMISSION_CREATE))],
        )
        async def create(
            dto: PermissionRequestDTO,
            service: PermissionService = Depends(get_permission_service),
        ) -> PermissionResponseDTO:
            return await service.create(dto)

        @router.get(
            "/{permission_id}",
            response_model=PermissionResponseDTO,
            summary="Busca uma permissão por id",
            dependencies=[Depends(require_permission(PERMISSION_READ))],
        )
        async def find_by_id(
            permission_id: UUID,
            service: PermissionService = Depends(get_permission_service),
        ) -> PermissionResponseDTO:
            return await service.find_by_id(permission_id)

        @router.get(
            "",
            response_model=PageResponse[PermissionResponseDTO],
            summary="Lista permissões (paginado)",
            dependencies=[Depends(require_permission(PERMISSION_READ))],
        )
        async def find_all(
            service: PermissionService = Depends(get_permission_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[PermissionResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{permission_id}",
            response_model=PermissionResponseDTO,
            summary="Atualiza uma permissão",
            dependencies=[Depends(require_permission(PERMISSION_UPDATE))],
        )
        async def update(
            permission_id: UUID,
            dto: PermissionRequestDTO,
            service: PermissionService = Depends(get_permission_service),
        ) -> PermissionResponseDTO:
            return await service.update(permission_id, dto)

        @router.delete(
            "/{permission_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove uma permissão",
            dependencies=[Depends(require_permission(PERMISSION_DELETE))],
        )
        async def delete(
            permission_id: UUID,
            service: PermissionService = Depends(get_permission_service),
        ) -> None:
            await service.delete(permission_id)
