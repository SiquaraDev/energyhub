"""Ponto de entrada da aplicação FastAPI do EnergyHub.

Monta routers, middlewares e handlers de erro; customiza o documento OpenAPI (metadados, esquema
`bearerAuth`, tags) da Fase 8; e inicializa o cache Redis (fastapi-cache2) no `lifespan` da Fase 9.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from energyhub.audit.presentation.router.audit_log_router import AuditLogRouter
from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.auth.presentation.exception.invalid_credentials_exception_handler import (
    invalid_credentials_exception_handler,
)
from energyhub.auth.presentation.router.auth_router import AuthRouter
from energyhub.auth.presentation.router.permission_router import PermissionRouter
from energyhub.auth.presentation.router.role_router import RoleRouter
from energyhub.auth.presentation.router.user_router import UserRouter
from energyhub.clients.presentation.router.client_router import ClientRouter
from energyhub.contracts.presentation.router.contract_router import ContractRouter
from energyhub.financial.presentation.router.financial_router import FinancialRouter
from energyhub.negotiations.presentation.router.negotiation_router import NegotiationRouter
from energyhub.notifications.presentation.router.notification_router import NotificationRouter
from energyhub.reports.presentation.router.report_router import ReportRouter
from energyhub.shared.domain.exception.domain_exception import DomainException
from energyhub.shared.infrastructure.cache.cache_config import CacheConfig
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings
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
    {"name": "Health", "description": "Verificações de disponibilidade (raiz e health check)."},
]

# Rotas públicas — não exigem token; a segurança global do OpenAPI é neutralizada nelas.
_PUBLIC_PATHS = {"/", "/health", "/api/v1/auth/login"}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Ciclo de vida da app: inicializa o cache Redis (fastapi-cache2) no startup.

    A conexão do `redis.asyncio.from_url` é preguiçosa — o startup não falha se o Redis estiver
    indisponível; o backend conecta na primeira operação de cache.
    """
    CacheConfig.init_cache()
    yield


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
        "url": "https://github.com/Matheus-Siquara/energyhub",
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
