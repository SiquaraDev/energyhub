"""DTO de resposta de usuário (a senha nunca é exposta)."""

from __future__ import annotations

from pydantic import Field

from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.shared.application.dto.base_dto import BaseDTO


class UserResponseDTO(BaseDTO):
    """Representação de saída de um usuário, com os papéis aninhados. **Sem** o campo `password`."""

    username: str
    email: str
    full_name: str | None = None
    active: bool = True
    roles: list[RoleResponseDTO] = Field(default_factory=list)
