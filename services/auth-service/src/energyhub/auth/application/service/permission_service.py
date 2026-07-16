"""Serviço de aplicação de `Permission`."""

from __future__ import annotations

from uuid import UUID

from fastapi_cache.decorator import cache

from energyhub.auth.application.dto.permission_request_dto import PermissionRequestDTO
from energyhub.auth.application.dto.permission_response_dto import PermissionResponseDTO
from energyhub.auth.application.mapper.permission_mapper import PermissionMapper
from energyhub.auth.domain.exception.permission_already_exists_exception import (
    PermissionAlreadyExistsException,
)
from energyhub.auth.domain.exception.permission_not_found_exception import (
    PermissionNotFoundException,
)
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.auth.infrastructure.persistence.permission_repository import PermissionRepository
from energyhub.auth.infrastructure.persistence.role_repository import RoleRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.cache_constants import CacheConstants
from energyhub.shared.infrastructure.cache.cache_config import id_key_builder, page_key_builder
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_cache
from energyhub.shared.infrastructure.messaging.audit_event import AuditEvent
from energyhub.shared.infrastructure.messaging.audit_event_producer import audit_event_producer
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.security.actor_context import get_current_actor


class PermissionService:
    """CRUD de permissões com unicidade de nome, e leitura das permissões de um papel."""

    def __init__(
        self,
        repository: PermissionRepository,
        mapper: PermissionMapper | None = None,
        role_repository: RoleRepository | None = None,
    ) -> None:
        self._repository = repository
        self._mapper = mapper or PermissionMapper()
        self._roles = role_repository

    async def create(self, dto: PermissionRequestDTO) -> PermissionResponseDTO:
        if await self._repository.exists_by_name(dto.name):
            raise PermissionAlreadyExistsException(f"Já existe permissão com o nome {dto.name}")
        saved = await self._repository.save(self._mapper.to_entity(dto))
        await invalidate_cache(CacheConstants.PERMISSIONS)
        await publish_safely(
            audit_event_producer.publish_audit(
                AuditEvent(
                    user_id=get_current_actor(),
                    action="CREATE",  # CREATE | UPDATE | DELETE — valores do enum AuditAction
                    entity_type="Permission",
                    entity_id=saved.id,
                    details={"name": saved.name},
                )
            ),
            event="audit",
        )
        return self._mapper.to_response_dto(saved)

    @cache(
        namespace=CacheConstants.PERMISSIONS,
        expire=CacheConstants.LONG_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_id(self, permission_id: UUID) -> PermissionResponseDTO:
        entity = await self._repository.find_by_id(permission_id)
        if entity is None:
            raise PermissionNotFoundException(f"Permissão {permission_id} não encontrada")
        return self._mapper.to_response_dto(entity)

    @cache(
        namespace=CacheConstants.PERMISSIONS,
        expire=CacheConstants.LONG_TTL,
        key_builder=page_key_builder,
    )
    async def find_all(self, page_request: PageRequest) -> PageResponse[PermissionResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    @cache(
        namespace=CacheConstants.PERMISSIONS,
        expire=CacheConstants.LONG_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_role_name(self, role_name: str) -> list[PermissionResponseDTO]:
        """Lista as permissões concedidas a um papel (carregadas eager via `selectin`)."""
        if self._roles is None:
            raise RuntimeError("find_by_role_name requer um RoleRepository injetado")
        role = await self._roles.find_by_name(role_name)
        if role is None:
            raise RoleNotFoundException(f"Papel {role_name} não encontrado")
        return [self._mapper.to_response_dto(permission) for permission in role.permissions]

    async def update(self, permission_id: UUID, dto: PermissionRequestDTO) -> PermissionResponseDTO:
        entity = await self._repository.find_by_id(permission_id)
        if entity is None:
            raise PermissionNotFoundException(f"Permissão {permission_id} não encontrada")
        entity.description = dto.description
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.PERMISSIONS)
        await publish_safely(
            audit_event_producer.publish_audit(
                AuditEvent(
                    user_id=get_current_actor(),
                    action="UPDATE",  # CREATE | UPDATE | DELETE — valores do enum AuditAction
                    entity_type="Permission",
                    entity_id=saved.id,
                    details={"name": saved.name},
                )
            ),
            event="audit",
        )
        return self._mapper.to_response_dto(saved)

    async def delete(self, permission_id: UUID) -> None:
        if not await self._repository.exists_by_id(permission_id):
            raise PermissionNotFoundException(f"Permissão {permission_id} não encontrada")
        await self._repository.delete_by_id(permission_id)
        await invalidate_cache(CacheConstants.PERMISSIONS)
        await publish_safely(
            audit_event_producer.publish_audit(
                AuditEvent(
                    user_id=get_current_actor(),
                    action="DELETE",  # CREATE | UPDATE | DELETE — valores do enum AuditAction
                    entity_type="Permission",
                    entity_id=permission_id,
                    details={},
                )
            ),
            event="audit",
        )
