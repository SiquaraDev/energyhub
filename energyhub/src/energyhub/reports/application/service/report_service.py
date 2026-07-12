"""Serviço de aplicação do agregado `Report` (regras de negócio sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from energyhub.reports.application.dto.report_request_dto import ReportRequestDTO
from energyhub.reports.application.dto.report_response_dto import ReportResponseDTO
from energyhub.reports.application.mapper.report_mapper import ReportMapper
from energyhub.reports.domain.exception.report_not_found_exception import (
    ReportNotFoundException,
)
from energyhub.reports.infrastructure.persistence.report_repository import ReportRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class ReportService:
    """CRUD de relatórios. Faz `flush` via repositório; o `commit` fica com a sessão por
    requisição (`get_session`)."""

    def __init__(self, repository: ReportRepository, mapper: ReportMapper | None = None) -> None:
        self._repository = repository
        self._mapper = mapper or ReportMapper()

    async def create(self, dto: ReportRequestDTO) -> ReportResponseDTO:
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, report_id: UUID) -> ReportResponseDTO:
        entity = await self._repository.find_by_id(report_id)
        if entity is None:
            raise ReportNotFoundException(f"Relatório {report_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[ReportResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, report_id: UUID, dto: ReportRequestDTO) -> ReportResponseDTO:
        entity = await self._repository.find_by_id(report_id)
        if entity is None:
            raise ReportNotFoundException(f"Relatório {report_id} não encontrado")
        entity.parameters = dto.parameters
        entity.file_path = dto.file_path
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def delete(self, report_id: UUID) -> None:
        if not await self._repository.exists_by_id(report_id):
            raise ReportNotFoundException(f"Relatório {report_id} não encontrado")
        await self._repository.delete_by_id(report_id)
