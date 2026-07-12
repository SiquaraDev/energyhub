"""Router REST do módulo `audit` (registro append-only + listagem paginada)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.audit.application.dto.audit_log_request_dto import AuditLogRequestDTO
from energyhub.audit.application.dto.audit_log_response_dto import AuditLogResponseDTO
from energyhub.audit.application.service.audit_log_service import AuditLogService
from energyhub.audit.application.usecase.create_audit_log_use_case import CreateAuditLogUseCase
from energyhub.audit.infrastructure.persistence.audit_log_repository import AuditLogRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_audit_log_service(session: AsyncSession = Depends(get_session)) -> AuditLogService:
    """Provedor do `AuditLogService` por requisição (repositório sobre a sessão)."""
    return AuditLogService(AuditLogRepository(session))


def get_create_audit_log_use_case(
    service: AuditLogService = Depends(get_audit_log_service),
) -> CreateAuditLogUseCase:
    """Provedor do caso de uso de registro de log de auditoria."""
    return CreateAuditLogUseCase(service)


class AuditLogRouter(BaseRouter):
    """Registra os endpoints REST de logs de auditoria sob `/api/v1/audit-logs`."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/audit-logs", tags=["audit"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=AuditLogResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Registra um log de auditoria",
            description="Registra um log de auditoria (recurso append-only).",
        )
        async def create(
            dto: AuditLogRequestDTO,
            use_case: CreateAuditLogUseCase = Depends(get_create_audit_log_use_case),
        ) -> AuditLogResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{audit_log_id}",
            response_model=AuditLogResponseDTO,
            summary="Busca um log de auditoria por id",
        )
        async def find_by_id(
            audit_log_id: UUID,
            service: AuditLogService = Depends(get_audit_log_service),
        ) -> AuditLogResponseDTO:
            return await service.find_by_id(audit_log_id)

        @router.get(
            "",
            response_model=PageResponse[AuditLogResponseDTO],
            summary="Lista logs de auditoria (paginado)",
        )
        async def find_all(
            service: AuditLogService = Depends(get_audit_log_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[AuditLogResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )
