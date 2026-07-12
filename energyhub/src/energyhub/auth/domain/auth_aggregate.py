from __future__ import annotations

from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User


class AuthAggregate:
    """Agregado de Autenticação — raiz User, fronteira de consistência com Role."""

    def __init__(self, user: User) -> None:
        self._user = user

    def add_role(self, role: Role) -> None:
        """Atribui um papel ao usuário (bidirecional), delegando à raiz."""
        self._user.add_role(role)
        self._user.update_timestamp()

    def remove_role(self, role: Role) -> None:
        """Remove um papel do usuário (bidirecional), delegando à raiz."""
        self._user.remove_role(role)
        self._user.update_timestamp()

    def get_user(self) -> User:
        """Retorna a raiz do agregado."""
        return self._user
