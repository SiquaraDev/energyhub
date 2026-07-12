"""DTO de resposta de permissão."""

from __future__ import annotations

from energyhub.shared.application.dto.base_dto import BaseDTO


class PermissionResponseDTO(BaseDTO):
    """Representação de saída de uma permissão."""

    name: str
    description: str | None = None
