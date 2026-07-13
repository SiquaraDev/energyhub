"""Fixtures compartilhadas dos testes do EnergyHub (Fase 13).

Organização:
- **Ambiente de teste** (task 2.2): aponta a aplicação para a infraestrutura de teste **antes** de
  as configurações serem carregadas, via `os.environ.setdefault` — respeitando variáveis já
  definidas, de modo que o mesmo conftest sirva à execução no host e dentro do container.
- **Cache em memória por teste**: os métodos de serviço decorados com `@cache` (fastapi-cache2) e o
  `invalidate_cache` das escritas precisam de um backend inicializado; um `InMemoryBackend` novo por
  teste os torna executáveis sem Redis e sem vazamento de estado entre testes (unidade).
- **Test doubles** (task 2.1): `email_service`, `notification_service` e `event_producer` como
  `AsyncMock` reutilizáveis — aguardáveis e com asserções de interação (`assert_called_once`).
- **Integração** (skip-guarded): `client` (FastAPI `TestClient`) e `session` (sessão async) pulam
  automaticamente quando a infraestrutura não está acessível (ex.: Postgres host→container no
  Windows), mantendo a suíte unitária 100% executável sem Docker.
"""

from __future__ import annotations

import os

# --- Ambiente de teste (task 2.2) --------------------------------------------------------------
# Definido no topo do módulo (antes de importar `settings`/`app`) para que a aplicação nunca
# conecte a um datastore de desenvolvimento/produção. Portas não-padrão do docker-compose.test.yml.
# NOTA: perfil de teste é `development` (guarda de produção não dispara). `SECRET_KEY` é um valor
# de teste dedicado (não é credencial de produção) e a senha da infra de teste NÃO usa o placeholder
# `energyhub123` — o repositório fica livre de credenciais placeholder ativas.
_TEST_ENV_DEFAULTS = {
    "DATABASE_URL": "postgresql+asyncpg://energyhub:eh_test_pw@localhost:5433/energyhub_test",
    "REDIS_URL": "redis://localhost:6380/0",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6380",
    "RABBITMQ_URL": "amqp://energyhub:eh_test_pw@localhost:5673/",
    "SECRET_KEY": "test-only-secret-key-not-for-production",
    "ENVIRONMENT": "development",
}
for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)

from collections.abc import AsyncIterator, Callable, Iterator  # noqa: E402
from typing import Any  # noqa: E402
from unittest.mock import AsyncMock  # noqa: E402

import pytest  # noqa: E402
import pytest_asyncio  # noqa: E402
from fastapi_cache import FastAPICache  # noqa: E402
from fastapi_cache.backends.inmemory import InMemoryBackend  # noqa: E402
from fastapi_cache.coder import PickleCoder  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool  # noqa: E402

from energyhub.config.settings import settings  # noqa: E402
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings  # noqa: E402


# --- Ambiente de teste: fixture session-scoped autouse (task 2.2) ------------------------------
@pytest.fixture(scope="session", autouse=True)
def _test_environment() -> Iterator[None]:
    """Garante (idempotente) que `DATABASE_URL`/`REDIS_URL`/`RABBITMQ_URL` apontam para a
    infraestrutura de teste durante toda a sessão, e apenas dentro do processo de teste."""
    for key, value in _TEST_ENV_DEFAULTS.items():
        os.environ.setdefault(key, value)
    yield


# --- Cache em memória por teste ----------------------------------------------------------------
@pytest.fixture(autouse=True)
def _cache_backend() -> Iterator[None]:
    """Inicializa um `InMemoryBackend` novo por teste (prefixo `energyhub`, `PickleCoder`).

    Torna os métodos `@cache` e `invalidate_cache` dos serviços executáveis sem Redis; como o
    backend é recriado a cada teste, leituras cacheadas não vazam entre testes.

    `FastAPICache.init` é no-op quando já inicializado, então `reset()` antes garante um backend
    limpo por teste. O `InMemoryBackend._store` é um dict **de classe** (compartilhado entre
    instâncias), então limpá-lo explicitamente evita que uma leitura cacheada vaze entre testes.
    """
    FastAPICache.reset()
    InMemoryBackend._store.clear()
    FastAPICache.init(InMemoryBackend(), prefix="energyhub", coder=PickleCoder)
    yield
    InMemoryBackend._store.clear()
    FastAPICache.reset()


# --- Test doubles para dependências externas (task 2.1) ----------------------------------------
@pytest.fixture
def email_service() -> AsyncMock:
    """Double aguardável do serviço de e-mail (dependência externa)."""
    return AsyncMock()


@pytest.fixture
def notification_service() -> AsyncMock:
    """Double aguardável do serviço de notificações (dependência externa)."""
    return AsyncMock()


@pytest.fixture
def event_producer() -> AsyncMock:
    """Double aguardável do produtor de eventos (RabbitMQ/Kafka)."""
    return AsyncMock()


# --- Harness de teste de componente de router (sem banco/rede) ---------------------------------
class _AllowAllUser:
    """`UserDetails` de teste que concede todas as permissões/papéis.

    Injetado no lugar de `get_current_user` para exercitar os routers (e os guards
    `require_permission`, que resolvem o usuário atual e checam `has_permission`) sem token nem
    banco — cobrindo a camada de apresentação com serviços mockados.
    """

    username = "tester"
    active = True
    roles: list[str] = []
    permissions: list[str] = []

    def has_permission(self, permission: str) -> bool:
        return True

    def has_role(self, role: str) -> bool:
        return True


@pytest.fixture
def router_client() -> Iterator[Callable[..., Any]]:
    """Fábrica que monta um app FastAPI mínimo com um router e overrides de dependência.

    Sempre sobrescreve `get_current_user` (→ usuário com todas as permissões); os demais overrides
    (provedores de serviço/caso de uso) são passados por teste. Não sobe o lifespan (sem infra).
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from energyhub.auth.infrastructure.security.current_user import get_current_user

    created: list[Any] = []

    def _build(router: Any, overrides: dict[Any, Any] | None = None) -> Any:
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[get_current_user] = _AllowAllUser
        for dependency, provider in (overrides or {}).items():
            app.dependency_overrides[dependency] = provider
        test_client = TestClient(app)
        created.append(test_client)
        return test_client

    yield _build
    for test_client in created:
        test_client.close()


# --- Integração (skip-guarded) -----------------------------------------------------------------
@pytest.fixture
def client() -> Iterator[object]:
    """Cliente de teste da aplicação FastAPI (inicializa o lifespan: banco, cache, mensageria...).

    Pula automaticamente se o lifespan não conseguir subir (infraestrutura indisponível).
    """
    from fastapi.testclient import TestClient

    from energyhub.main import app

    # raise_server_exceptions=False: erros de servidor (ex.: banco indisponível em tempo de
    # requisição) viram respostas 500 em vez de propagarem — o teste de integração então trata o
    # status e pula, em vez de estourar com traceback no host.
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    except Exception as exc:  # noqa: BLE001 — qualquer falha de boot vira skip (infra ausente)
        pytest.skip(f"Aplicação não pôde inicializar (infraestrutura indisponível): {exc}")


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Sessão async com isolamento por teste (rollback ao final).

    Engine próprio por teste com `NullPool` (o pytest-asyncio usa um event loop por teste; um engine
    compartilhado reaproveitaria conexões asyncpg de outro loop). Pula se o banco não responder.
    """
    configure_mappings()
    engine = create_async_engine(settings.database_url, poolclass=NullPool)
    try:
        async with engine.connect() as probe:
            await probe.rollback()
    except (SQLAlchemyError, OSError) as exc:
        await engine.dispose()
        pytest.skip(f"Postgres indisponível ({settings.database_url}): {exc}")

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as sess:
        try:
            yield sess
        finally:
            await sess.rollback()
    await engine.dispose()
