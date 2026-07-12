"""Router REST do módulo `reports` (CRUD + listagem paginada)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.reports.application.dto.report_request_dto import ReportRequestDTO
from energyhub.reports.application.dto.report_response_dto import ReportResponseDTO
from energyhub.reports.application.service.report_service import ReportService
from energyhub.reports.application.usecase.create_report_use_case import CreateReportUseCase
from energyhub.reports.infrastructure.persistence.report_repository import ReportRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_report_service(session: AsyncSession = Depends(get_session)) -> ReportService:
    """Provedor do `ReportService` por requisição (repositório sobre a sessão)."""
    return ReportService(ReportRepository(session))


def get_create_report_use_case(
    service: ReportService = Depends(get_report_service),
) -> CreateReportUseCase:
    """Provedor do caso de uso de criação de relatório."""
    return CreateReportUseCase(service)


class ReportRouter(BaseRouter):
    """Registra os endpoints REST de relatórios sob `/api/v1/reports`."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/reports", tags=["reports"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=ReportResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria um relatório",
            description="Cria um relatório sob demanda (status inicial PENDING).",
        )
        async def create(
            dto: ReportRequestDTO,
            use_case: CreateReportUseCase = Depends(get_create_report_use_case),
        ) -> ReportResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{report_id}",
            response_model=ReportResponseDTO,
            summary="Busca um relatório por id",
        )
        async def find_by_id(
            report_id: UUID,
            service: ReportService = Depends(get_report_service),
        ) -> ReportResponseDTO:
            return await service.find_by_id(report_id)

        @router.get(
            "",
            response_model=PageResponse[ReportResponseDTO],
            summary="Lista relatórios (paginado)",
        )
        async def find_all(
            service: ReportService = Depends(get_report_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[ReportResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{report_id}",
            response_model=ReportResponseDTO,
            summary="Atualiza um relatório",
        )
        async def update(
            report_id: UUID,
            dto: ReportRequestDTO,
            service: ReportService = Depends(get_report_service),
        ) -> ReportResponseDTO:
            return await service.update(report_id, dto)

        @router.delete(
            "/{report_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove um relatório",
        )
        async def delete(
            report_id: UUID,
            service: ReportService = Depends(get_report_service),
        ) -> None:
            await service.delete(report_id)
