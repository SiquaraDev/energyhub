"""DTO de resposta de permissão."""

from __future__ import annotations

from pydantic import Field

from energyhub.shared.application.dto.base_dto import BaseDTO


class PermissionResponseDTO(BaseDTO):
    """Representação de saída de uma permissão."""

    name: str = Field(..., description="Nome da permissão", examples=["USER_CREATE"])
    description: str | None = Field(
        None, description="Descrição da permissão", examples=["Permite criar usuários"]
    )
