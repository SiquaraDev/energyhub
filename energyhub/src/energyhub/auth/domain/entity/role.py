from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.auth.domain.entity.permission import Permission
    from energyhub.auth.domain.entity.user import User


@dataclass(kw_only=True)
class Role(BaseEntity):
    """Papel (perfil de acesso) que agrupa permissões e é atribuído a usuários."""

    name: str
    description: str | None = None
    permissions: list[Permission] = field(default_factory=list, compare=False, repr=False)
    users: list[User] = field(default_factory=list, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name or not self.name.strip():
            raise ValidationException("name do papel não pode ser vazio")

    def add_permission(self, permission: Permission) -> None:
        """Adiciona uma permissão ao papel (idempotente)."""
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove uma permissão do papel."""
        if permission in self.permissions:
            self.permissions.remove(permission)
