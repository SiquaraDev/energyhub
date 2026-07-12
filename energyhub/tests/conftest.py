"""Fixtures compartilhadas dos testes do EnergyHub."""

from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from energyhub.config.settings import settings
from energyhub.main import app
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente de teste da aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Sessão async com isolamento por teste.

    Cria um engine próprio por teste com `NullPool`: como o pytest-asyncio usa um event loop
    por teste, um engine compartilhado reaproveitaria conexões asyncpg de outro loop (erro
    "another operation is in progress"). Como o `save` faz `flush` (não `commit`) e os testes
    não commitam, o `rollback` ao final descarta tudo. Requer o schema da Fase 4 aplicado.
    """
    configure_mappings()
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as sess:
        try:
            yield sess
        finally:
            await sess.rollback()
    await engine.dispose()
