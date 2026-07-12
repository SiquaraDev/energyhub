"""Caso de uso: registrar log de auditoria."""

from __future__ import annotations

from energyhub.audit.application.dto.audit_log_request_dto import AuditLogRequestDTO
from energyhub.audit.application.dto.audit_log_response_dto import AuditLogResponseDTO
from energyhub.audit.application.service.audit_log_service import AuditLogService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateAuditLogUseCase(UseCase[AuditLogRequestDTO, AuditLogResponseDTO]):
    """Orquestra o registro de um log de auditoria delegando ao `AuditLogService`."""

    def __init__(self, service: AuditLogService) -> None:
        self._service = service

    async def execute(self, input_data: AuditLogRequestDTO) -> AuditLogResponseDTO:
        return await self._service.create(input_data)
