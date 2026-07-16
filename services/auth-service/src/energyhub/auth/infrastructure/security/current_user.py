"""Dependência FastAPI `get_current_user`: resolve o bearer token no usuário autenticado.

Usa `HTTPBearer(auto_error=False)` para que a **ausência** de token retorne 401 (e não o 403
padrão do Starlette). Extrai o `sub` via `JwtService`, recarrega o usuário por username (papéis e
permissões vêm eager via `lazy="selectin"`) e devolve um `UserDetails`. Token inválido/ausente ou
subject sem usuário correspondente → 401 com `WWW-Authenticate: Bearer`.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.auth.infrastructure.security.jwt_service import JwtService
from energyhub.auth.infrastructure.security.user_details import UserDetails
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.actor_context import set_current_actor

# auto_error=False: tratamos nós mesmos a ausência de credenciais (→ 401, não 403).
# scheme_name/bearerFormat: alinham o esquema de segurança do OpenAPI com o `bearerAuth` (JWT)
# documentado no `custom_openapi()` (Fase 8) — mesmo nome nas operações e em securitySchemes.
_bearer_scheme = HTTPBearer(scheme_name="bearerAuth", bearerFormat="JWT", auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserDetails:
    """Resolve o token em `UserDetails`; 401 se ausente/inválido ou sem usuário correspondente."""
    if credentials is None:
        raise _UNAUTHORIZED

    username = JwtService().extract_username(credentials.credentials)
    if username is None:
        raise _UNAUTHORIZED

    user = await UserRepository(session).find_by_username(username)
    if user is None:
        raise _UNAUTHORIZED

    details = UserDetails(user)
    # Publica o ator no contexto da requisição: alimenta o `user_id` do `AuditEvent` nos serviços de
    # aplicação sem propagar o usuário autenticado como parâmetro por todas as camadas.
    set_current_actor(details.id)
    return details
