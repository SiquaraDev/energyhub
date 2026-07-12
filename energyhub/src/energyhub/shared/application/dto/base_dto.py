"""DTO base da camada de aplicação."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class BaseDTO:
    """Campos comuns de transporte (opcionais) para DTOs de entrada/saída."""

    id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
