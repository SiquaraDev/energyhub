from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.clients.domain.entity.client import Client


@dataclass(kw_only=True, eq=False)
class Contact(BaseEntity):
    """Contato associado a um cliente."""

    client_id: UUID
    name: str
    type: ContactType
    email: str | None = None
    phone: str | None = None
    position: str | None = None
    client: Client | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name or not self.name.strip():
            raise ValidationException("name não pode ser vazio")
