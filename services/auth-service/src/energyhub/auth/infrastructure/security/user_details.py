"""`UserDetails`: visão de segurança do usuário autenticado (Fase 7).

Encapsula a entidade `User` e expõe apenas o que os guards de autorização precisam — `username`,
`active`, os nomes dos papéis e as permissões **achatadas** através de todos os papéis. Mantém a
entidade ORM fora da camada de apresentação e centraliza o achatamento papel→permissão.
"""

from __future__ import annotations

from energyhub.auth.domain.entity.user import User


class UserDetails:
    """Wrapper somente-leitura sobre `User` com a identidade e as concessões do chamador."""

    def __init__(self, user: User) -> None:
        self._user = user

    @property
    def user(self) -> User:
        """A entidade `User` subjacente."""
        return self._user

    @property
    def username(self) -> str:
        return self._user.username

    @property
    def active(self) -> bool:
        return self._user.active

    @property
    def roles(self) -> list[str]:
        """Nomes dos papéis atribuídos ao usuário."""
        return [role.name for role in self._user.roles]

    @property
    def permissions(self) -> list[str]:
        """Nomes das permissões, achatados (sem duplicatas) através de todos os papéis."""
        seen: dict[str, None] = {}
        for role in self._user.roles:
            for permission in role.permissions:
                seen.setdefault(permission.name, None)
        return list(seen)

    def has_permission(self, permission: str) -> bool:
        """`True` se o usuário possui a permissão nomeada."""
        return permission in self.permissions

    def has_role(self, role: str) -> bool:
        """`True` se o usuário possui o papel nomeado."""
        return role in self.roles
