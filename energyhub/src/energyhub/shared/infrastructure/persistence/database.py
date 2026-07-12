"""Base declarativa do SQLAlchemy e metadata compartilhada pelas migrações."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todo o mapeamento ORM.

    Os modelos ORM concretos são adicionados na Fase 5 (Persistência). Nesta
    fase, `Base.metadata` existe para servir de `target_metadata` ao Alembic —
    as migrações da Fase 4 são escritas à mão (sem autogenerate), portanto a
    metadata permanece vazia até os modelos serem mapeados.
    """
