"""Guards de autorização RBAC como *dependency factories* do FastAPI (Fase 7).

`require_permission`/`require_role` produzem dependências que resolvem o usuário atual via
`get_current_user` (portanto uma requisição não autenticada é barrada com 401 **antes** de qualquer
checagem) e liberam a rota apenas se o usuário possui a concessão exigida; caso contrário, 403.

Ficam na camada compartilhada por serem transversais — consumidos por routers de qualquer módulo.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Depends, HTTPException, status

from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.auth.infrastructure.security.user_details import UserDetails

_Guard = Callable[[UserDetails], Awaitable[UserDetails]]


def require_permission(permission: str) -> _Guard:
    """Dependência que exige a permissão nomeada; 403 se o usuário atual não a possui."""

    async def _guard(current_user: UserDetails = Depends(get_current_user)) -> UserDetails:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada: requer '{permission}'",
            )
        return current_user

    return _guard


def require_role(role: str) -> _Guard:
    """Dependência que exige o papel nomeado; 403 se o usuário atual não o possui."""

    async def _guard(current_user: UserDetails = Depends(get_current_user)) -> UserDetails:
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado: requer o papel '{role}'",
            )
        return current_user

    return _guard
