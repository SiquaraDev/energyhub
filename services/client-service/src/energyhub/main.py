"""Ponto de entrada do **client-service** (Fase 15).

Microsserviço do contexto **Clients**. Depende do Auth via `AuthClient` (HTTP) para resolver o usuário
atual (antes era in-process). Dono do seu banco (`clientdb`); registra-se no Consul no startup.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from energyhub.clients.infrastructure.messaging.client_event_producer import client_event_producer
from energyhub.clients.presentation.router.client_router import ClientRouter
from energyhub.config import settings
from energyhub.discovery import deregister_from_consul, register_with_consul
from energyhub.service_clients.auth_client import auth_client
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.infrastructure.cache.cache_config import CacheConfig
from energyhub.shared.infrastructure.messaging.audit_event_producer import audit_event_producer
from energyhub.shared.infrastructure.messaging.rabbitmq_config import setup_queues
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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup: cache, schema, filas (best-effort), registro no Consul. Shutdown: desregistro +
    fechamento dos clientes HTTP e produtores (libera pools de conexão)."""
    global _service_id
    CacheConfig.init_cache()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    try:
        await setup_queues()
    except Exception as error:  # noqa: BLE001
        logger.warning("Topologia RabbitMQ não preparada: %s", error)

    _service_id = register_with_consul(
        name=settings.app_name,
        port=settings.app_port,
        address=settings.service_host,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
        tags=[
            "traefik.enable=true",
            "traefik.http.routers.clients.rule=PathPrefix(`/api/v1/clients`)",
            "traefik.http.routers.clients.entrypoints=web",
            "traefik.http.routers.clients.middlewares=eh-ratelimit,eh-auth",
        ],
    )

    yield

    deregister_from_consul(
        service_id=_service_id,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
    )
    await auth_client.close()  # libera o pool httpx (§8.4)
    try:
        await client_event_producer.disconnect()
    except Exception as error:  # noqa: BLE001
        logger.warning("Falha ao encerrar ClientEventProducer: %s", error)
    try:
        await audit_event_producer.disconnect()
    except Exception as error:  # noqa: BLE001
        logger.warning("Falha ao encerrar AuditEventProducer: %s", error)


app = FastAPI(
    title="EnergyHub — Client Service",
    version=settings.app_version,
    lifespan=lifespan,
    description="Microsserviço de clientes e contatos.",
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

app.include_router(ClientRouter().get_router())


@app.get("/", tags=["Health"], summary="Raiz do serviço")
def read_root() -> dict[str, str]:
    return {"service": settings.app_name}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
