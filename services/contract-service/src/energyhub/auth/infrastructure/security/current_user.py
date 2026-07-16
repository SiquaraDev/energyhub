"""Dependência `get_current_user` do client-service (Fase 15).

**Substitui a chamada in-process ao Auth** (que carregava o usuário do banco) por uma chamada de rede
via `AuthClient`: decodifica o bearer token localmente (mesma `SECRET_KEY`), extrai o `sub` (username)
e resolve o usuário — com papéis/permissões — no `auth-service`. Token ausente/inválido ou usuário
inexistente/indisponível → 401.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from energyhub.auth.infrastructure.security.jwt_service import JwtService
from energyhub.auth.infrastructure.security.user_details import UserDetails
from energyhub.service_clients.auth_client import auth_client
from energyhub.shared.infrastructure.security.actor_context import set_current_actor

_bearer_scheme = HTTPBearer(scheme_name="bearerAuth", bearerFormat="JWT", auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não autenticado",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserDetails:
    """Resolve o token em `UserDetails` via `auth-service`; 401 se ausente/inválido/indisponível."""
    if credentials is None:
        raise _UNAUTHORIZED

    username = JwtService().extract_username(credentials.credentials)
    if username is None:
        raise _UNAUTHORIZED

    # Chamada de rede ao Auth (resiliente: timeout + retry + fallback None).
    user_data = await auth_client.get_user_by_username(username)
    if user_data is None:
        raise _UNAUTHORIZED

    details = UserDetails(user_data)
    # Alimenta o `user_id` do `AuditEvent` sem propagar o usuário como parâmetro pelas camadas:
    # os routers usam esta dependência apenas como guard, então o ator viaja por ContextVar.
    set_current_actor(details.id)
    return details
