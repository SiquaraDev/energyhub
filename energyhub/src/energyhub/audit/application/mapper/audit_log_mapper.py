"""Mapper entre a entidade `AuditLog` e seus DTOs."""

from __future__ import annotations

from energyhub.audit.application.dto.audit_log_request_dto import AuditLogRequestDTO
from energyhub.audit.application.dto.audit_log_response_dto import AuditLogResponseDTO
from energyhub.audit.domain.entity.audit_log import AuditLog


class AuditLogMapper:
    """Ponto único de tradução entidade↔DTO para `AuditLog`."""

    @staticmethod
    def to_entity(dto: AuditLogRequestDTO) -> AuditLog:
        """Constrói um `AuditLog` a partir do request DTO (id/timestamps gerados ao persistir)."""
        return AuditLog(
            user_id=dto.user_id,
            action=dto.action,
            entity_type=dto.entity_type,
            entity_id=dto.entity_id,
            details=dto.details,
        )

    @staticmethod
    def to_response_dto(entity: AuditLog) -> AuditLogResponseDTO:
        """Constrói o response DTO da entidade (`from_attributes`)."""
        return AuditLogResponseDTO.model_validate(entity)
