"""Mapper entre `Role` e seus DTOs."""

from __future__ import annotations

from energyhub.auth.application.dto.role_request_dto import RoleRequestDTO
from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.auth.domain.entity.role import Role


class RoleMapper:
    """Ponto único de tradução entidade↔DTO para `Role` (permissões resolvidas no serviço)."""

    @staticmethod
    def to_entity(dto: RoleRequestDTO) -> Role:
        return Role(name=dto.name, description=dto.description)

    @staticmethod
    def to_response_dto(entity: Role) -> RoleResponseDTO:
        return RoleResponseDTO.model_validate(entity)
