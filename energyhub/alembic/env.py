"""Ambiente de execução do Alembic para o EnergyHub.

A URL do banco e a metadata são obtidas da aplicação (fonte única):
- `settings.database_url` → conexão;
- `Base.metadata` → `target_metadata`.

Suporta migrações online (conexão viva, driver assíncrono `asyncpg` com `NullPool`)
e offline (geração de SQL com `literal_binds`, sem conexão).
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from energyhub.config.settings import settings
from energyhub.shared.infrastructure.persistence.database import Base

# Objeto de configuração do Alembic (dá acesso ao alembic.ini).
config = context.config

# Fonte única da URL: sobrescreve o placeholder do alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Logging conforme o alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata-alvo para o contexto de migração (autogenerate chega na Fase 5).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa as migrações em modo offline (emite SQL, sem conectar).

    Usa `literal_binds` para renderizar valores inline, permitindo gerar o SQL
    completo (`alembic upgrade head --sql`) sem acesso ao banco.
    """
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configura o contexto sobre uma conexão síncrona e roda as migrações."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Cria um engine assíncrono (NullPool) e aplica as migrações online."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Executa as migrações em modo online sobre uma conexão viva."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
