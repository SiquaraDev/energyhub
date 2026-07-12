from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.clients.domain.entity.contact import Contact


@dataclass(kw_only=True, eq=False)
class Client(BaseEntity):
    """Cliente do sistema (raiz do ClientAggregate)."""

    cnpj: str
    corporate_name: str
    trade_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    active: bool = True
    contacts: list[Contact] = field(default_factory=list, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.cnpj or not self.cnpj.strip():
            raise ValidationException("cnpj não pode ser vazio")
        if not self.corporate_name or not self.corporate_name.strip():
            raise ValidationException("corporate_name não pode ser vazio")
