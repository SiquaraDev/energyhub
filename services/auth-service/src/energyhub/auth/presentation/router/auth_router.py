"""Router REST de autenticação (`/api/v1/auth`) — rota **pública** (sem token)."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.application.dto.login_request_dto import LoginRequestDTO
from energyhub.auth.application.dto.login_response_dto import LoginResponseDTO
from energyhub.auth.application.service.authentication_service import AuthenticationService
from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.shared.constant.application_constants import API_V1_PREFIX
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.response.openapi_responses import BAD_REQUEST, UNAUTHORIZED
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_authentication_service(
    session: AsyncSession = Depends(get_session),
) -> AuthenticationService:
    """Provedor do `AuthenticationService` por requisição."""
    return AuthenticationService(UserRepository(session))


class AuthRouter(BaseRouter):
    """Endpoints de autenticação. Este grupo NÃO exige token (login é público)."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "/login",
            response_model=LoginResponseDTO,
            summary="Autentica um usuário e emite um token JWT",
            description=(
                "Recebe `username`/`password`, valida as credenciais e devolve um token de "
                "acesso `bearer` com o perfil do usuário. Credenciais inválidas retornam 401."
            ),
            responses={**BAD_REQUEST, **UNAUTHORIZED},
        )
        async def login(
            dto: LoginRequestDTO,
            service: AuthenticationService = Depends(get_authentication_service),
        ) -> LoginResponseDTO:
            return await service.login(dto)
