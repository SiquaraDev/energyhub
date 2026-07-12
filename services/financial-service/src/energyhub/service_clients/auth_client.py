"""Cliente HTTP para o contexto **Auth** (Fase 15).

Substitui a antiga chamada in-process ao módulo `auth` (carregar o usuário atual do banco) por uma
chamada de rede tipada ao `auth-service`, preservando a direção de dependência (Clients → Auth).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from energyhub.service_clients.base import ServiceClient


class AuthClient(ServiceClient):
    """Expõe as operações que este serviço precisa do contexto Auth."""

    def __init__(self) -> None:
        super().__init__("auth-service", 8001)

    async def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        """Busca um usuário (com papéis/permissões) pelo username; `None` se ausente/indisponível."""
        return await self._get(f"/internal/users/by-username/{username}")

    async def get_user_by_id(self, user_id: UUID | str) -> dict[str, Any] | None:
        """Busca um usuário pelo id; `None` se ausente/indisponível."""
        return await self._get(f"/internal/users/{user_id}")


# Singleton do serviço (fecha o pool no shutdown, ver main.lifespan).
auth_client = AuthClient()
