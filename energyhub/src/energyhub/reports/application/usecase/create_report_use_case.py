"""Caso de uso: criar relatório."""

from __future__ import annotations

from energyhub.reports.application.dto.report_request_dto import ReportRequestDTO
from energyhub.reports.application.dto.report_response_dto import ReportResponseDTO
from energyhub.reports.application.service.report_service import ReportService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateReportUseCase(UseCase[ReportRequestDTO, ReportResponseDTO]):
    """Orquestra a criação de um relatório delegando ao `ReportService` (sem lógica própria)."""

    def __init__(self, service: ReportService) -> None:
        self._service = service

    async def execute(self, input_data: ReportRequestDTO) -> ReportResponseDTO:
        return await self._service.create(input_data)
