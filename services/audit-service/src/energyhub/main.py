"""Ponto de entrada do **audit-service** (Fase 15).

Microsserviço do contexto **Audit** (trilha append-only). Diferente dos demais: **consome eventos**
do barramento (RabbitMQ) — sem dependência síncrona de negócio — além de expor o router de leitura.
Dono do seu banco (`auditdb`). Registra-se no Consul.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from energyhub.audit.infrastructure.messaging.audit_consumer import AuditConsumer
from energyhub.audit.presentation.router.audit_log_router import AuditLogRouter
from energyhub.config import settings
from energyhub.discovery import deregister_from_consul, register_with_consul
from energyhub.service_clients.auth_client import auth_client
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.infrastructure.cache.cache_config import CacheConfig
from energyhub.shared.infrastructure.persistence.database import engine
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings, metadata
from energyhub.shared.presentation.exception.domain_exception_handler import (
    domain_exception_handler,
)
from energyhub.shared.presentation.exception.global_exception_handler import (
    global_exception_handler,
)
from energyhub.shared.presentation.exception.request_validation_exception_handler import (
    request_validation_exception_handler,
)

logger = logging.getLogger(__name__)

configure_mappings()

_service_id: str = ""


async def _run_consumer() -> None:
    """Task de fundo: consome eventos de auditoria do RabbitMQ (tolerante a broker ausente)."""
    try:
        await AuditConsumer().start_consuming()
    except asyncio.CancelledError:
        raise
    except Exception as error:  # noqa: BLE001 — broker indisponível não derruba o serviço
        logger.warning("Consumidor de auditoria encerrou: %s", error)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    global _service_id
    CacheConfig.init_cache()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    consumer_task = asyncio.create_task(_run_consumer())

    _service_id = register_with_consul(
        name=settings.app_name,
        port=settings.app_port,
        address=settings.service_host,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
        tags=[
            "traefik.enable=true",
            "traefik.http.routers.audit.rule=PathPrefix(`/api/v1/audit-logs`)",
            "traefik.http.routers.audit.entrypoints=web",
            "traefik.http.routers.audit.middlewares=eh-ratelimit,eh-auth",
        ],
    )

    yield

    consumer_task.cancel()
    deregister_from_consul(
        service_id=_service_id,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
    )
    await auth_client.close()


app = FastAPI(
    title="EnergyHub — Audit Service",
    version=settings.app_version,
    lifespan=lifespan,
    description="Microsserviço de auditoria (consumidor de eventos + trilha append-only).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,  # type: ignore[arg-type]
)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(AuditLogRouter().get_router())


@app.get("/", tags=["Health"], summary="Raiz do serviço")
def read_root() -> dict[str, str]:
    return {"service": settings.app_name}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
