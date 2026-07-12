"""Testes de INTEGRAÇÃO do `ClientRepository` contra um PostgreSQL real (Fase 13 · task 5).

Fonte do banco (nesta ordem):
1. `EH_TEST_DATABASE_URL` — URL async explícita (ex.: execução in-container na rede Docker, onde o
   Postgres é acessível; caminho usado no Windows, onde host→container falha).
2. `EH_ENABLE_TESTCONTAINERS=1` — provisiona um `PostgresContainer` efêmero via Testcontainers
   (caminho padrão em ambientes com Docker acessível do processo de teste).
Sem nenhum dos dois, os testes são pulados (a suíte unitária roda sem Docker). O container/engine é
**module-scoped** (criado uma vez) e o schema é materializado via `metadata.create_all`. Cada teste
é isolado por rollback da sessão.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from energyhub.clients.domain.entity.client import Client
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings, metadata

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def _database_url() -> Iterator[str]:
    """Resolve a URL do Postgres de teste (env explícita ou Testcontainers); pula se ausente."""
    url = os.environ.get("EH_TEST_DATABASE_URL")
    if url:
        yield url
        return

    if not os.environ.get("EH_ENABLE_TESTCONTAINERS"):
        pytest.skip("defina EH_TEST_DATABASE_URL ou EH_ENABLE_TESTCONTAINERS=1 para a integração")

    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:  # pragma: no cover - ambiente sem a lib
        pytest.skip("testcontainers indisponível")

    try:
        with PostgresContainer("postgres:16-alpine", driver="asyncpg") as container:
            yield container.get_connection_url()
    except Exception as exc:  # noqa: BLE001 - falha ao subir container vira skip
        pytest.skip(f"não foi possível iniciar o PostgresContainer: {exc}")


@pytest_asyncio.fixture(scope="module")
async def _engine(_database_url: str) -> AsyncIterator[AsyncEngine]:
    """Engine async module-scoped ligado ao container; materializa o schema; descarta ao final."""
    configure_mappings()
    engine = create_async_engine(_database_url, poolclass=NullPool)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
    except (SQLAlchemyError, OSError) as exc:
        await engine.dispose()
        pytest.skip(f"Postgres indisponível ({_database_url}): {exc}")
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def repo_session(_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Sessão isolada por teste (rollback ao final — o `save` só faz flush, não commit)."""
    maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        try:
            yield session
        finally:
            await session.rollback()


async def test_should_save_and_find_client_by_id(repo_session: AsyncSession) -> None:
    repo = ClientRepository(repo_session)
    saved = await repo.save(
        Client(cnpj="11222333000181", corporate_name="Usina Integração", city="Campinas")
    )

    assert saved.id is not None
    fetched = await repo.find_by_id(saved.id)
    assert fetched is not None
    assert fetched.cnpj == "11222333000181"
    assert fetched.corporate_name == "Usina Integração"
    assert fetched.city == "Campinas"


async def test_should_resolve_custom_finder_find_by_cnpj(repo_session: AsyncSession) -> None:
    repo = ClientRepository(repo_session)
    await repo.save(Client(cnpj="11444777000161", corporate_name="Usina Beta"))

    found = await repo.find_by_cnpj("11444777000161")
    assert found is not None
    assert found.corporate_name == "Usina Beta"
    assert await repo.exists_by_cnpj("11444777000161") is True
    assert await repo.find_by_cnpj("99999999999999") is None
