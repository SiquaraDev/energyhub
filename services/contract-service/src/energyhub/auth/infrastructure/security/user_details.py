"""`UserDetails` do client-service (Fase 15).

Visão somente-leitura do usuário autenticado, construída a partir da **resposta JSON do auth-service**
(não mais da entidade ORM local — este serviço não é dono da tabela `users`). Expõe o que os guards
de autorização precisam: username, ativo, papéis e permissões achatadas.
"""

from __future__ import annotations

from typing import Any


class UserDetails:
    """Wrapper sobre o payload do usuário devolvido pelo auth-service."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def username(self) -> str:
        return str(self._data.get("username", ""))

    @property
    def active(self) -> bool:
        return bool(self._data.get("active", False))

    @property
    def roles(self) -> list[str]:
        return [role.get("name", "") for role in self._data.get("roles", [])]

    @property
    def permissions(self) -> list[str]:
        """Permissões achatadas (sem duplicatas) através de todos os papéis."""
        seen: dict[str, None] = {}
        for role in self._data.get("roles", []):
            for permission in role.get("permissions", []):
                seen.setdefault(permission.get("name", ""), None)
        return list(seen)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        return role in self.roles
