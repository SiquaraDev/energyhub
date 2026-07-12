from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.auth.domain.entity.role import Role


@dataclass(kw_only=True)
class User(BaseEntity):
    """Usuário do sistema (raiz do AuthAggregate)."""

    username: str
    password: str
    email: str
    full_name: str | None = None
    active: bool = True
    roles: list[Role] = field(default_factory=list, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.username or not self.username.strip():
            raise ValidationException("username não pode ser vazio")
        if "@" not in self.email:
            raise ValidationException("email inválido")

    def add_role(self, role: Role) -> None:
        """Adiciona um papel ao usuário (bidirecional)."""
        if role not in self.roles:
            self.roles.append(role)
        if self not in role.users:
            role.users.append(self)

    def remove_role(self, role: Role) -> None:
        """Remove um papel do usuário (bidirecional)."""
        if role in self.roles:
            self.roles.remove(role)
        if self in role.users:
            role.users.remove(self)
