"""Router REST de usuários (`/api/v1/users`)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.application.dto.user_request_dto import UserRequestDTO
from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.application.service.user_service import UserService
from energyhub.auth.application.usecase.create_user_use_case import CreateUserUseCase
from energyhub.auth.infrastructure.persistence.role_repository import RoleRepository
from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.constant.permissions import (
    USER_CREATE,
    USER_DELETE,
    USER_READ,
    USER_UPDATE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    """Provedor do `UserService` por requisição."""
    return UserService(UserRepository(session), RoleRepository(session))


def get_create_user_use_case(
    service: UserService = Depends(get_user_service),
) -> CreateUserUseCase:
    """Provedor do caso de uso de criação de usuário."""
    return CreateUserUseCase(service)


class UserRouter(BaseRouter):
    """Endpoints REST de usuários."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/users",
            tags=["auth"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=UserResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria um usuário",
            description="Cria um usuário (senha é hasheada; papéis por id). Rejeita duplicados.",
            dependencies=[Depends(require_permission(USER_CREATE))],
        )
        async def create(
            dto: UserRequestDTO,
            use_case: CreateUserUseCase = Depends(get_create_user_use_case),
        ) -> UserResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{user_id}",
            response_model=UserResponseDTO,
            summary="Busca um usuário por id",
            dependencies=[Depends(require_permission(USER_READ))],
        )
        async def find_by_id(
            user_id: UUID,
            service: UserService = Depends(get_user_service),
        ) -> UserResponseDTO:
            return await service.find_by_id(user_id)

        @router.get(
            "",
            response_model=PageResponse[UserResponseDTO],
            summary="Lista usuários (paginado)",
            dependencies=[Depends(require_permission(USER_READ))],
        )
        async def find_all(
            service: UserService = Depends(get_user_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[UserResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{user_id}",
            response_model=UserResponseDTO,
            summary="Atualiza um usuário",
            dependencies=[Depends(require_permission(USER_UPDATE))],
        )
        async def update(
            user_id: UUID,
            dto: UserRequestDTO,
            service: UserService = Depends(get_user_service),
        ) -> UserResponseDTO:
            return await service.update(user_id, dto)

        @router.delete(
            "/{user_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove um usuário",
            dependencies=[Depends(require_permission(USER_DELETE))],
        )
        async def delete(
            user_id: UUID,
            service: UserService = Depends(get_user_service),
        ) -> None:
            await service.delete(user_id)
