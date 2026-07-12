"""Mapper entre entidades de `reports` e seus DTOs."""

from __future__ import annotations

from energyhub.reports.application.dto.report_request_dto import ReportRequestDTO
from energyhub.reports.application.dto.report_response_dto import ReportResponseDTO
from energyhub.reports.domain.entity.report import Report


class ReportMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Report`."""

    @staticmethod
    def to_entity(dto: ReportRequestDTO) -> Report:
        """Constrói um `Report` a partir do request DTO (id/timestamps gerados na persistência)."""
        return Report(
            report_type=dto.report_type,
            generated_by=dto.generated_by,
            parameters=dto.parameters,
            file_path=dto.file_path,
        )

    @staticmethod
    def to_response_dto(entity: Report) -> ReportResponseDTO:
        """Constrói o response DTO da entidade (via from_attributes)."""
        return ReportResponseDTO.model_validate(entity)
