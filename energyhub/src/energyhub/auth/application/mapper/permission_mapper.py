"""Mapper entre `Permission` e seus DTOs."""

from __future__ import annotations

from energyhub.auth.application.dto.permission_request_dto import PermissionRequestDTO
from energyhub.auth.application.dto.permission_response_dto import PermissionResponseDTO
from energyhub.auth.domain.entity.permission import Permission


class PermissionMapper:
    """Ponto único de tradução entidade↔DTO para `Permission`."""

    @staticmethod
    def to_entity(dto: PermissionRequestDTO) -> Permission:
        return Permission(name=dto.name, description=dto.description)

    @staticmethod
    def to_response_dto(entity: Permission) -> PermissionResponseDTO:
        return PermissionResponseDTO.model_validate(entity)
