"""DTO base da camada de aplicação (Pydantic)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """Campos de auditoria comuns aos DTOs de **resposta** (`id`, `created_at`, `updated_at`).

    `from_attributes=True` permite construir o DTO diretamente de uma entidade de domínio
    (`SomeResponseDTO.model_validate(entity)`), convertendo inclusive relações aninhadas quando
    o campo é tipado como outro DTO de resposta.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
