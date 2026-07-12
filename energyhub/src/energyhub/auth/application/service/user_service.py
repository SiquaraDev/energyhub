"""Serviço de aplicação de `User` (hash de senha + atribuição de papéis por id)."""

from __future__ import annotations

from uuid import UUID

from fastapi_cache.decorator import cache

from energyhub.auth.application.dto.user_request_dto import UserRequestDTO
from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.application.mapper.user_mapper import UserMapper
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.auth.domain.exception.user_already_exists_exception import (
    UserAlreadyExistsException,
)
from energyhub.auth.domain.exception.user_not_found_exception import UserNotFoundException
from energyhub.auth.infrastructure.messaging.user_event_producer import UserEventProducer
from energyhub.auth.infrastructure.persistence.role_repository import RoleRepository
from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.cache_constants import CacheConstants
from energyhub.shared.infrastructure.cache.cache_config import id_key_builder, page_key_builder
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_cache
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.security.password_hasher import hash_password


class UserService:
    """CRUD de usuários: unicidade username/e-mail, hash de senha e atribuição de papéis.

    `username`/`email` são imutáveis no update (chaves únicas). A senha é sempre re-hasheada.
    Após cada escrita persistida publica o evento de domínio correspondente (RabbitMQ), como
    efeito colateral não-bloqueante — uma falha de broker é logada, não desfaz a escrita.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        mapper: UserMapper | None = None,
        event_producer: UserEventProducer | None = None,
    ) -> None:
        self._users = user_repository
        self._roles = role_repository
        self._mapper = mapper or UserMapper()
        self._producer = event_producer

    async def _resolve_roles(self, role_ids: list[UUID]) -> list[Role]:
        resolved: list[Role] = []
        for role_id in role_ids:
            role = await self._roles.find_by_id(role_id)
            if role is None:
                raise RoleNotFoundException(f"Papel {role_id} não encontrado")
            resolved.append(role)
        return resolved

    async def create(self, dto: UserRequestDTO) -> UserResponseDTO:
        if await self._users.exists_by_username(dto.username):
            raise UserAlreadyExistsException(f"Já existe usuário com o username {dto.username}")
        if await self._users.exists_by_email(dto.email):
            raise UserAlreadyExistsException(f"Já existe usuário com o e-mail {dto.email}")
        user = self._mapper.to_entity(dto)
        user.password = hash_password(dto.password)
        user.active = dto.active
        for role in await self._resolve_roles(dto.role_ids):
            user.roles.append(role)
        saved = await self._users.save(user)
        await invalidate_cache(CacheConstants.USERS)
        response = self._mapper.to_response_dto(saved)
        if self._producer is not None:
            await publish_safely(
                self._producer.publish_user_created(response), event="user.created"
            )
        return response

    @cache(
        namespace=CacheConstants.USERS,
        expire=CacheConstants.DEFAULT_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_id(self, user_id: UUID) -> UserResponseDTO:
        entity = await self._users.find_by_id(user_id)
        if entity is None:
            raise UserNotFoundException(f"Usuário {user_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    @cache(
        namespace=CacheConstants.USERS,
        expire=CacheConstants.DEFAULT_TTL,
        key_builder=page_key_builder,
    )
    async def find_all(self, page_request: PageRequest) -> PageResponse[UserResponseDTO]:
        content, total = await self._users.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, user_id: UUID, dto: UserRequestDTO) -> UserResponseDTO:
        user = await self._users.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(f"Usuário {user_id} não encontrado")
        user.full_name = dto.full_name
        user.active = dto.active
        user.password = hash_password(dto.password)
        user.roles = await self._resolve_roles(dto.role_ids)
        user.update_timestamp()
        saved = await self._users.save(user)
        await invalidate_cache(CacheConstants.USERS)
        response = self._mapper.to_response_dto(saved)
        if self._producer is not None:
            await publish_safely(
                self._producer.publish_user_updated(response), event="user.updated"
            )
        return response

    async def delete(self, user_id: UUID) -> None:
        if not await self._users.exists_by_id(user_id):
            raise UserNotFoundException(f"Usuário {user_id} não encontrado")
        await self._users.delete_by_id(user_id)
        await invalidate_cache(CacheConstants.USERS)
        if self._producer is not None:
            await publish_safely(self._producer.publish_user_deleted(user_id), event="user.deleted")
