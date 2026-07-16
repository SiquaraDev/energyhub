"""Ponto de entrada do **auth-service** (Fase 15).

Microsserviço FastAPI independente do contexto **Auth** (identidade + RBAC). Expõe os routers de
autenticação/usuários/papéis/permissões, um `/health`, e se **registra no Consul** no startup (com
health check HTTP), desregistrando no shutdown. Dono do seu próprio banco (`authdb`).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.auth.infrastructure.messaging.user_event_producer import user_event_producer
from energyhub.auth.presentation.exception.invalid_credentials_exception_handler import (
    invalid_credentials_exception_handler,
)
from energyhub.auth.presentation.router.auth_router import AuthRouter
from energyhub.auth.presentation.router.internal_router import router as internal_users_router
from energyhub.auth.presentation.router.permission_router import PermissionRouter
from energyhub.auth.presentation.router.role_router import RoleRouter
from energyhub.auth.presentation.router.user_router import UserRouter
from energyhub.config import settings
from energyhub.discovery import deregister_from_consul, register_with_consul
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
    """Startup: cache, schema, filas (best-effort) e registro no Consul. Shutdown: desregistro."""
    global _service_id
    CacheConfig.init_cache()
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    try:
        await setup_queues()
    except Exception as error:  # noqa: BLE001 — broker indisponível não derruba o startup
        logger.warning("Topologia RabbitMQ não preparada: %s", error)

    _service_id = register_with_consul(
        name=settings.app_name,
        port=settings.app_port,
        address=settings.service_host,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
        tags=[
            "traefik.enable=true",
            "traefik.http.routers.auth.rule=PathPrefix(`/api/v1/auth`)"
            " || PathPrefix(`/api/v1/users`) || PathPrefix(`/api/v1/roles`)"
            " || PathPrefix(`/api/v1/permissions`)",
            "traefik.http.routers.auth.entrypoints=web",
            "traefik.http.routers.auth.middlewares=eh-ratelimit",
            # Definições dos middlewares de borda (rate limit + forwardAuth):
            "traefik.http.middlewares.eh-ratelimit.ratelimit.average=100",
            "traefik.http.middlewares.eh-ratelimit.ratelimit.burst=50",
            "traefik.http.middlewares.eh-auth.forwardauth.address"
            "=http://auth-service:8001/internal/auth/verify",
        ],
    )

    yield

    deregister_from_consul(
        service_id=_service_id,
        consul_host=settings.consul_host,
        consul_port=settings.consul_port,
    )
    try:
        await user_event_producer.disconnect()
    except Exception as error:  # noqa: BLE001
        logger.warning("Falha ao encerrar UserEventProducer: %s", error)
    try:
        await audit_event_producer.disconnect()
    except Exception as error:  # noqa: BLE001
        logger.warning("Falha ao encerrar AuditEventProducer: %s", error)


app = FastAPI(
    title="EnergyHub — Auth Service",
    version=settings.app_version,
    lifespan=lifespan,
    description="Microsserviço de identidade e RBAC (login, usuários, papéis, permissões).",
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
    InvalidCredentialsException,
    invalid_credentials_exception_handler,  # type: ignore[arg-type]
)
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,  # type: ignore[arg-type]
)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(AuthRouter().get_router())
app.include_router(UserRouter().get_router())
app.include_router(RoleRouter().get_router())
app.include_router(PermissionRouter().get_router())
# Rotas internas (não publicadas pelo gateway) — resolução de usuário para outros serviços.
app.include_router(internal_users_router)


@app.get("/", tags=["Health"], summary="Raiz do serviço")
def read_root() -> dict[str, str]:
    """Endpoint raiz — identificação do serviço."""
    return {"service": settings.app_name}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Health check (liveness) — usado pelo Consul e pelo gateway."""
    return {"status": "healthy"}
