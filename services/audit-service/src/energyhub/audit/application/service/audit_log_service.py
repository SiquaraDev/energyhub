"""Serviço de aplicação de `AuditLog` (recurso append-only: sem update/delete)."""

from __future__ import annotations

from uuid import UUID

from energyhub.audit.application.dto.audit_log_request_dto import AuditLogRequestDTO
from energyhub.audit.application.dto.audit_log_response_dto import AuditLogResponseDTO
from energyhub.audit.application.mapper.audit_log_mapper import AuditLogMapper
from energyhub.audit.domain.exception.audit_log_not_found_exception import (
    AuditLogNotFoundException,
)
from energyhub.audit.infrastructure.persistence.audit_log_repository import AuditLogRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class AuditLogService:
    """Registro e leitura de logs de auditoria. Recurso **append-only**: cria e consulta,
    mas não atualiza nem remove. Faz `flush` via repositório; o `commit` fica com a sessão
    por requisição (`get_session`)."""

    def __init__(
        self, repository: AuditLogRepository, mapper: AuditLogMapper | None = None
    ) -> None:
        self._repository = repository
        self._mapper = mapper or AuditLogMapper()

    async def create(self, dto: AuditLogRequestDTO) -> AuditLogResponseDTO:
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, audit_log_id: UUID) -> AuditLogResponseDTO:
        entity = await self._repository.find_by_id(audit_log_id)
        if entity is None:
            raise AuditLogNotFoundException(f"Log de auditoria {audit_log_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[AuditLogResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)
