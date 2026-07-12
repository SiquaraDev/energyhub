"""Ponto de entrada da aplicação FastAPI do EnergyHub."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from energyhub.audit.presentation.router.audit_log_router import AuditLogRouter
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
from energyhub.shared.infrastructure.persistence.mapping import configure_mappings
from energyhub.shared.presentation.exception.domain_exception_handler import (
    domain_exception_handler,
)

# Registra e resolve os mappers ORM (Fase 5) no import da app, de modo que qualquer
# erro de mapeamento/relacionamento apareça imediatamente no startup.
configure_mappings()

app = FastAPI(
    title="EnergyHub API",
    description="Plataforma de negociação de energia — API REST (Clean Architecture · DDD).",
    version="0.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Traduz exceções de domínio em respostas HTTP padronizadas (404/409/422).
app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]

# Routers dos módulos de negócio.
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


@app.get("/")
def read_root() -> dict[str, str]:
    """Endpoint raiz."""
    return {"message": "EnergyHub API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check da aplicação."""
    return {"status": "healthy"}
