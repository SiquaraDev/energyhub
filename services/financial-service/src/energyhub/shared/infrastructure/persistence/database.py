"""Configuração de persistência: Base declarativa, engine async e sessão.

O `Base` ancora a `metadata`/`registry` usados pelo **mapeamento imperativo** das entidades
(ver `mapping.py`): as entidades de domínio permanecem _dataclasses_ puras e são mapeadas às
tabelas da Fase 4 sem importar SQLAlchemy, preservando a regra de dependência da Clean Architecture.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from energyhub.config import settings


class Base(DeclarativeBase):
    """Base declarativa compartilhada; sua `metadata`/`registry` ancora todo o mapeamento ORM.

    As migrações (Fase 4) são a fonte de verdade do schema; os mapeamentos imperativos
    (Fase 5) são reconciliados a elas, sem `--autogenerate`.
    """


# Engine assíncrono único, ligado às settings (asyncpg). `echo` segue `settings.debug`.
engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)

# Fábrica de sessões: `expire_on_commit=False` mantém os atributos acessíveis após o commit.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependência de sessão por requisição (unidade de trabalho).

    Cede uma `AsyncSession`, faz `commit` ao final se nada falhar e `rollback` em caso de
    exceção. Como os repositórios fazem `flush` (não `commit`), a fronteira transacional fica
    aqui: várias operações num mesmo request compõem uma única transação.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
