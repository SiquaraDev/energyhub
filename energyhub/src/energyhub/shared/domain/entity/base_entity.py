"""Entidade base do domínio (raiz comum de todas as entidades)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    """Retorna o instante atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


@dataclass(kw_only=True)
class BaseEntity:
    """Campos comuns a todas as entidades: identidade e timestamps de auditoria.

    Os campos são keyword-only (`kw_only=True`) para que subclasses possam declarar
    campos obrigatórios sem esbarrar na ordenação de campos com/sem default do dataclass.
    """

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        """Inicializa campos que tenham sido explicitamente passados como None."""
        if self.id is None:
            self.id = uuid4()
        if self.created_at is None:
            self.created_at = _utcnow()
        if self.updated_at is None:
            self.updated_at = _utcnow()

    def update_timestamp(self) -> None:
        """Atualiza `updated_at` para o instante atual (chamar ao mutar a entidade)."""
        self.updated_at = _utcnow()
