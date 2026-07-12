"""Rotas internas do auth-service (Fase 15) — consumidas por outros serviços via `AuthClient`.

Expõem a busca de usuário (por username / id) com papéis e permissões, para que os demais serviços
resolvam o usuário atual sem ler a tabela `users` (que é propriedade exclusiva do Auth). São
**não autenticadas** por design: ficam apenas na rede interna (não são publicadas pelo gateway) e
servem justamente para o passo de autenticação dos outros serviços.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.application.mapper.user_mapper import UserMapper
from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.auth.infrastructure.security.jwt_service import JwtService
from energyhub.shared.infrastructure.persistence.database import get_session

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.get("/auth/verify", summary="Valida o bearer token (para o forwardAuth do gateway)")
def verify_token(authorization: str | None = Header(default=None)) -> dict[str, str]:
    """Valida o JWT do cabeçalho `Authorization`; 200 se válido, 401 caso contrário.

    Usado pelo middleware `forwardAuth` do Traefik para autenticar na **borda** (Fase 15): o gateway
    encaminha os cabeçalhos da requisição para cá antes de rotear às rotas protegidas.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
    token = authorization.split(" ", 1)[1]
    username = JwtService().extract_username(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return {"status": "ok", "username": username}


@router.get("/users/by-username/{username}", response_model=UserResponseDTO)
async def get_user_by_username(
    username: str, session: AsyncSession = Depends(get_session)
) -> UserResponseDTO:
    """Usuário (com papéis/permissões) por username — usado por `AuthClient.get_user_by_username`."""
    user = await UserRepository(session).find_by_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return UserMapper.to_response_dto(user)


@router.get("/users/{user_id}", response_model=UserResponseDTO)
async def get_user_by_id(
    user_id: UUID, session: AsyncSession = Depends(get_session)
) -> UserResponseDTO:
    """Usuário por id — usado por `AuthClient.get_user_by_id`."""
    user = await UserRepository(session).find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return UserMapper.to_response_dto(user)
