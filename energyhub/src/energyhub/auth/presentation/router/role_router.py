"""Router REST de papéis (`/api/v1/roles`)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.application.dto.role_request_dto import RoleRequestDTO
from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.auth.application.service.role_service import RoleService
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
    ROLE_CREATE,
    ROLE_DELETE,
    ROLE_READ,
    ROLE_UPDATE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.response.openapi_responses import (
    AUTH_ERRORS,
    BAD_REQUEST,
    CONFLICT,
    NOT_FOUND,
)
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_role_service(session: AsyncSession = Depends(get_session)) -> RoleService:
    """Provedor do `RoleService` por requisição."""
    return RoleService(RoleRepository(session), PermissionRepository(session))


class RoleRouter(BaseRouter):
    """Endpoints REST de papéis."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/roles",
            tags=["Roles"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=RoleResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria um papel",
            description="Cria um papel com permissões por id (rejeita nomes duplicados).",
            dependencies=[Depends(require_permission(ROLE_CREATE))],
            responses={**BAD_REQUEST, **CONFLICT, **AUTH_ERRORS},
        )
        async def create(
            dto: RoleRequestDTO,
            service: RoleService = Depends(get_role_service),
        ) -> RoleResponseDTO:
            return await service.create(dto)

        @router.get(
            "/{role_id}",
            response_model=RoleResponseDTO,
            summary="Busca um papel por id",
            description="Retorna um papel pelo seu identificador único.",
            dependencies=[Depends(require_permission(ROLE_READ))],
            responses={**NOT_FOUND, **AUTH_ERRORS},
        )
        async def find_by_id(
            role_id: UUID,
            service: RoleService = Depends(get_role_service),
        ) -> RoleResponseDTO:
            return await service.find_by_id(role_id)

        @router.get(
            "",
            response_model=PageResponse[RoleResponseDTO],
            summary="Lista papéis (paginado)",
            description="Lista os papéis de forma paginada e ordenável.",
            dependencies=[Depends(require_permission(ROLE_READ))],
            responses={**AUTH_ERRORS},
        )
        async def find_all(
            service: RoleService = Depends(get_role_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[RoleResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{role_id}",
            response_model=RoleResponseDTO,
            summary="Atualiza um papel",
            description="Atualiza os dados e permissões de um papel existente pelo seu id.",
            dependencies=[Depends(require_permission(ROLE_UPDATE))],
            responses={**BAD_REQUEST, **NOT_FOUND, **AUTH_ERRORS},
        )
        async def update(
            role_id: UUID,
            dto: RoleRequestDTO,
            service: RoleService = Depends(get_role_service),
        ) -> RoleResponseDTO:
            return await service.update(role_id, dto)

        @router.delete(
            "/{role_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove um papel",
            description="Remove um papel existente pelo seu id.",
            dependencies=[Depends(require_permission(ROLE_DELETE))],
            responses={**NOT_FOUND, **AUTH_ERRORS},
        )
        async def delete(
            role_id: UUID,
            service: RoleService = Depends(get_role_service),
        ) -> None:
            await service.delete(role_id)
