"""DTO de resposta de usuário (a senha nunca é exposta)."""

from __future__ import annotations

from pydantic import Field

from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.shared.application.dto.base_dto import BaseDTO


class UserResponseDTO(BaseDTO):
    """Representação de saída de um usuário, com os papéis aninhados. **Sem** o campo `password`."""

    username: str = Field(..., description="Nome de usuário (único)", examples=["operador01"])
    email: str = Field(..., description="E-mail do usuário", examples=["usuario@energyhub.example"])
    full_name: str | None = Field(None, description="Nome completo", examples=["Operador da Silva"])
    active: bool = Field(True, description="Indica se o usuário está ativo", examples=[True])
    roles: list[RoleResponseDTO] = Field(
        default_factory=list, description="Papéis atribuídos ao usuário"
    )
