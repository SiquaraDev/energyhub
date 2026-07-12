"""Serviço de aplicação de `Role` (resolve permissões por id — associação M2M)."""

from __future__ import annotations

from uuid import UUID

from energyhub.auth.application.dto.role_request_dto import RoleRequestDTO
from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.auth.application.mapper.role_mapper import RoleMapper
from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.exception.permission_not_found_exception import (
    PermissionNotFoundException,
)
from energyhub.auth.domain.exception.role_already_exists_exception import (
    RoleAlreadyExistsException,
)
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.auth.infrastructure.persistence.permission_repository import PermissionRepository
from energyhub.auth.infrastructure.persistence.role_repository import RoleRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


class RoleService:
    """CRUD de papéis com unicidade de nome e atribuição de permissões por id."""

    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
        mapper: RoleMapper | None = None,
    ) -> None:
        self._roles = role_repository
        self._permissions = permission_repository
        self._mapper = mapper or RoleMapper()

    async def _resolve_permissions(self, permission_ids: list[UUID]) -> list[Permission]:
        resolved: list[Permission] = []
        for permission_id in permission_ids:
            permission = await self._permissions.find_by_id(permission_id)
            if permission is None:
                raise PermissionNotFoundException(f"Permissão {permission_id} não encontrada")
            resolved.append(permission)
        return resolved

    async def create(self, dto: RoleRequestDTO) -> RoleResponseDTO:
        if await self._roles.exists_by_name(dto.name):
            raise RoleAlreadyExistsException(f"Já existe papel com o nome {dto.name}")
        role = self._mapper.to_entity(dto)
        for permission in await self._resolve_permissions(dto.permission_ids):
            role.permissions.append(permission)
        saved = await self._roles.save(role)
        return self._mapper.to_response_dto(saved)

    async def find_by_id(self, role_id: UUID) -> RoleResponseDTO:
        entity = await self._roles.find_by_id(role_id)
        if entity is None:
            raise RoleNotFoundException(f"Papel {role_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    async def find_by_name(self, name: str) -> RoleResponseDTO:
        """Busca um papel pelo nome (ex.: `ADMIN`); erro de recurso-não-encontrado se ausente."""
        entity = await self._roles.find_by_name(name)
        if entity is None:
            raise RoleNotFoundException(f"Papel {name} não encontrado")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[RoleResponseDTO]:
        content, total = await self._roles.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, role_id: UUID, dto: RoleRequestDTO) -> RoleResponseDTO:
        role = await self._roles.find_by_id(role_id)
        if role is None:
            raise RoleNotFoundException(f"Papel {role_id} não encontrado")
        role.description = dto.description
        role.permissions = await self._resolve_permissions(dto.permission_ids)
        role.update_timestamp()
        saved = await self._roles.save(role)
        return self._mapper.to_response_dto(saved)

    async def delete(self, role_id: UUID) -> None:
        if not await self._roles.exists_by_id(role_id):
            raise RoleNotFoundException(f"Papel {role_id} não encontrado")
        await self._roles.delete_by_id(role_id)
