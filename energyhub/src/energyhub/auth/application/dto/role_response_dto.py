"""DTO de resposta de papel (role)."""

from __future__ import annotations

from pydantic import Field

from energyhub.auth.application.dto.permission_response_dto import PermissionResponseDTO
from energyhub.shared.application.dto.base_dto import BaseDTO


class RoleResponseDTO(BaseDTO):
    """Representação de saída de um papel, com as permissões aninhadas."""

    name: str
    description: str | None = None
    permissions: list[PermissionResponseDTO] = Field(default_factory=list)
