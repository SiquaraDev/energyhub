from __future__ import annotations

from dataclasses import dataclass

from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException


@dataclass(kw_only=True)
class Permission(BaseEntity):
    """Permissão atribuível a um papel (ex.: 'contracts:read')."""

    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name or not self.name.strip():
            raise ValidationException("name da permissão não pode ser vazio")
