"""Entidade base do domínio (raiz comum de todas as entidades)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def _utcnow() -> datetime:
    """Retorna o instante atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


@dataclass(kw_only=True, eq=False)
class BaseEntity:
    """Campos comuns a todas as entidades: identidade e timestamps de auditoria.

    Os campos são keyword-only (`kw_only=True`) para que subclasses possam declarar
    campos obrigatórios sem esbarrar na ordenação de campos com/sem default do dataclass.

    A igualdade é **por identidade** (`id`), não por valor de campos (`eq=False`): entidades
    são iguais quando têm o mesmo `id`, independentemente dos demais atributos — a semântica
    correta de *entidade* em DDD (diferente dos *value objects*, que comparam por valor). Isso
    também as torna hasheáveis, requisito para o mapeamento ORM (Fase 5). Subclasses devem
    manter `@dataclass(kw_only=True, eq=False)` para herdar esta semântica.
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

    def __eq__(self, other: object) -> bool:
        """Igualdade por identidade: mesmo tipo e mesmo `id`."""
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        """Hash pela identidade (`id`), estável para uso em coleções e no ORM."""
        return hash(self.id)
