"""Ponto de entrada da aplicação FastAPI do EnergyHub.

Monta routers, middlewares e handlers de erro; customiza o documento OpenAPI (metadados, esquema
`bearerAuth`, tags) da Fase 8; inicializa o cache Redis (fastapi-cache2) no `lifespan` da Fase 9;
prepara a mensageria (Fase 10) e os índices de busca (Fase 11); e instrumenta métricas Prometheus
(`/metrics`, métricas de negócio/recursos) da Fase 12.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from energyhub.audit.presentation.router.audit_log_router import AuditLogRouter
from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.auth.infrastructure.messaging.user_event_producer import user_event_producer
from energyhub.auth.presentation.exception.invalid_credentials_exception_handler import (
    invalid_credentials_exception_handler,
)
from energyhub.auth.presentation.router.auth_router import AuthRouter
from energyhub.auth.presentation.router.permission_router import PermissionRouter
from energyhub.auth.presentation.router.role_router import RoleRouter
from energyhub.auth.presentation.router.user_router import UserRouter
from energyhub.clients.infrastructure.messaging.client_event_producer import client_event_producer
from energyhub.clients.infrastructure.search.client_document import ClientDocument
from energyhub.clients.presentation.router.client_router import ClientRouter
from energyhub.clients.presentation.router.client_search_router import ClientSearchRouter
from energyhub.config.settings import settings
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.infrastructure.search.contract_document import ContractDocument
from energyhub.contracts.presentation.router.contract_router import ContractRouter
from energyhub.financial.presentation.router.financial_router import FinancialRouter
from energyhub.negotiations.presentation.router.negotiation_router import NegotiationRouter
from energyhub.notifications.presentation.router.notification_router import NotificationRouter
from energyhub.reports.presentation.router.report_router import ReportRouter
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.infrastructure.cache.cache_config import CacheConfig
from energyhub.shared.infrastructure.messaging.kafka_config import KafkaConfig
from energyhub.shared.infrastructure.messaging.kafka_event_producer import kafka_event_producer
from energyhub.shared.infrastructure.messaging.rabbitmq_config import setup_queues
from energyhub.shared.infrastructure.metrics.business_metrics import business_metrics
from energyhub.shared.infrastructure.metrics.metrics_config import set_application_info
from energyhub.shared.infrastructure.metrics.system_metrics import register_system_metrics
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings
from energyhub.shared.infrastructure.search.elasticsearch_config import ElasticsearchConfig
from energyhub.shared.presentation.exception.domain_exception_handler import (
    domain_exception_handler,
)
from energyhub.shared.presentation.exception.global_exception_handler import (
    global_exception_handler,
)
from energyhub.shared.presentation.exception.request_validation_exception_handler import (
    request_validation_exception_handler,
)
from energyhub.shared.presentation.router.cache_router import CacheRouter

logger = logging.getLogger(__name__)

# Registra e resolve os mappers ORM (Fase 5) no import da app, de modo que qualquer
# erro de mapeamento/relacionamento apareça imediatamente no startup.
configure_mappings()

# Metadados das tags do OpenAPI (agrupam as operações por área na UI de docs).
_OPENAPI_TAGS: list[dict[str, str]] = [
    {"name": "Authentication", "description": "Login e emissão de token JWT (rota pública)."},
    {"name": "Users", "description": "Gestão de usuários do sistema."},
    {"name": "Roles", "description": "Papéis (perfis de acesso) que agrupam permissões."},
    {"name": "Permissions", "description": "Permissões atribuíveis a papéis."},
    {"name": "Clients", "description": "Clientes e seus contatos."},
    {"name": "Contracts", "description": "Contratos de energia."},
    {"name": "Negotiations", "description": "Negociações e transações de energia."},
    {"name": "Financial", "description": "Faturas e pagamentos."},
    {"name": "Audit", "description": "Trilha de auditoria (append-only)."},
    {"name": "Notifications", "description": "Notificações do sistema."},
    {"name": "Reports", "description": "Relatórios do negócio."},
    {"name": "Cache", "description": "Administração do cache (estatísticas e limpeza)."},
    {"name": "Search", "description": "Busca full-text e filtros (Elasticsearch)."},
    {"name": "Health", "description": "Verificações de disponibilidade (raiz e health check)."},
]

# Rotas públicas — não exigem token; a segurança global do OpenAPI é neutralizada nelas.
_PUBLIC_PATHS = {"/", "/health", "/api/v1/auth/login"}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Ciclo de vida: cache (F9), mensageria (F10), busca (F11) e métricas (F12).

    - **Startup:** inicializa o cache Redis (conexão preguiçosa); declara filas/tópicos e índices de
      busca de forma idempotente (*best-effort* — um serviço indisponível apenas gera aviso, não
      derruba o startup); e prepara as métricas (`application_info`, séries de negócio em zero,
      coletor de recursos do host).
    - **Shutdown:** encerra as conexões dos produtores compartilhados.
    """
    CacheConfig.init_cache()
    try:
        await setup_queues()
    except Exception as error:  # broker indisponível não deve impedir o startup
        logger.warning("Topologia RabbitMQ não preparada (broker indisponível?): %s", error)
    try:
        await KafkaConfig.create_topics()
    except Exception as error:  # broker indisponível não deve impedir o startup
        logger.warning("Tópicos Kafka não preparados (broker indisponível?): %s", error)
    try:
        ElasticsearchConfig.create_indices([ClientDocument, ContractDocument])
    except Exception as error:  # Elasticsearch indisponível não deve impedir o startup
        logger.warning("Índices Elasticsearch não preparados (ES indisponível?): %s", error)

    # Métricas (Fase 12): info da app + séries de negócio em zero + coletor de recursos do host.
    set_application_info(settings.app_name, settings.environment, settings.app_version)
    business_metrics.initialize([status.value for status in ContractStatus])
    register_system_metrics()

    yield

    for closer, name in (
        (user_event_producer.disconnect(), "UserEventProducer"),
        (client_event_producer.disconnect(), "ClientEventProducer"),
        (kafka_event_producer.stop(), "KafkaEventProducer"),
    ):
        try:
            await closer
        except Exception as error:  # encerramento best-effort
            logger.warning("Falha ao encerrar %s: %s", name, error)


app = FastAPI(
    title="EnergyHub API",
    lifespan=lifespan,
    description=(
        "Plataforma de negociação de energia — API REST (Clean Architecture · DDD).\n\n"
        "**Autenticação:** obtenha um token em `POST /api/v1/auth/login` e envie-o como "
        "`Authorization: Bearer <token>`. Sem token → **401**; sem permissão → **403**.\n\n"
        "Veja `docs/API_ERRORS.md` (catálogo de erros) e `docs/API_EXAMPLES.md` (exemplos `curl`)."
    ),
    version="0.8.0",
    openapi_tags=_OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Handlers de exceção → corpos de erro padronizados e documentados.
app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(
    InvalidCredentialsException,
    invalid_credentials_exception_handler,  # type: ignore[arg-type]
)
# Validação de schema da requisição (Pydantic) → 400 ValidationErrorResponse (sobrescreve o 422).
app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,  # type: ignore[arg-type]
)
# Qualquer exceção não tratada → 500 ErrorResponse.
app.add_exception_handler(Exception, global_exception_handler)

# Rota pública de autenticação (login) — registrada sem dependência de token.
app.include_router(AuthRouter().get_router())

# Routers dos módulos de negócio (protegidos por JWT + permissão).
app.include_router(UserRouter().get_router())
app.include_router(RoleRouter().get_router())
app.include_router(PermissionRouter().get_router())
app.include_router(ClientRouter().get_router())
app.include_router(ContractRouter().get_router())
app.include_router(NegotiationRouter().get_router())
app.include_router(FinancialRouter().get_router())
app.include_router(AuditLogRouter().get_router())
app.include_router(NotificationRouter().get_router())
app.include_router(ReportRouter().get_router())

# Router de administração do cache (Fase 9) — protegido por CACHE_MANAGE.
app.include_router(CacheRouter().get_router())

# Router de busca de clientes (Fase 11) — Elasticsearch, sob /api/v1/search/clients.
app.include_router(ClientSearchRouter().get_router())

# Instrumentação Prometheus (Fase 12): métricas HTTP padrão (contagem, latência, in-progress) +
# endpoint /metrics. O próprio /metrics é excluído da instrumentação (não infla as métricas).
_instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=False,
    should_group_untemplated=True,
    should_instrument_requests_inprogress=True,
    inprogress_name="fastapi_requests_inprogress",
    inprogress_labels=True,
    excluded_handlers=["/metrics"],
)
_instrumentator.add(
    metrics.requests(metric_name="fastapi_requests_total"),
    metrics.latency(metric_name="fastapi_request_duration_seconds"),
)
_instrumentator.instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=True, tags=["Health"]
)


def custom_openapi() -> dict[str, Any]:
    """Constrói (uma vez) e cacheia o documento OpenAPI, injetando metadados e segurança JWT."""
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    schema["info"]["contact"] = {
        "name": "Equipe EnergyHub",
        "url": "https://github.com/SiquaraDev/energyhub",
        "email": "contato@energyhub.example",
    }
    schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
    # Esquema de segurança JWT + requisito global (rotas públicas são neutralizadas abaixo).
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "Token JWT obtido em `POST /api/v1/auth/login`. "
            "Envie-o no cabeçalho `Authorization: Bearer <token>`."
        ),
    }
    schema["security"] = [{"bearerAuth": []}]
    for path in _PUBLIC_PATHS:
        for operation in schema.get("paths", {}).get(path, {}).values():
            if isinstance(operation, dict):
                operation["security"] = []

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/", tags=["Health"], summary="Raiz da API")
def read_root() -> dict[str, str]:
    """Endpoint raiz — mensagem de identificação da API."""
    return {"message": "EnergyHub API"}


@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict[str, str]:
    """Health check da aplicação (liveness)."""
    return {"status": "healthy"}
