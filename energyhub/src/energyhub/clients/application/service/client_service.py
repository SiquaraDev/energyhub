"""Serviço de aplicação do agregado `Client` (regras de negócio sobre o repositório da Fase 5)."""

from __future__ import annotations

from uuid import UUID

from fastapi_cache.decorator import cache

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.mapper.client_mapper import ClientMapper
from energyhub.clients.domain.exception.client_already_exists_exception import (
    ClientAlreadyExistsException,
)
from energyhub.clients.domain.exception.client_not_found_exception import ClientNotFoundException
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.cache_constants import CacheConstants
from energyhub.shared.infrastructure.cache.cache_config import id_key_builder, page_key_builder
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_cache


class ClientService:
    """CRUD de clientes com checagens de existência/unicidade. Faz `flush` via repositório;
    o `commit` fica com a sessão por requisição (`get_session`)."""

    def __init__(self, repository: ClientRepository, mapper: ClientMapper | None = None) -> None:
        self._repository = repository
        self._mapper = mapper or ClientMapper()

    async def create(self, dto: ClientRequestDTO) -> ClientResponseDTO:
        if await self._repository.exists_by_cnpj(dto.cnpj):
            raise ClientAlreadyExistsException(f"Já existe um cliente com o CNPJ {dto.cnpj}")
        entity = self._mapper.to_entity(dto)
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CLIENTS)
        return self._mapper.to_response_dto(saved)

    @cache(
        namespace=CacheConstants.CLIENTS,
        expire=CacheConstants.SHORT_TTL,
        key_builder=id_key_builder,
    )
    async def find_by_id(self, client_id: UUID) -> ClientResponseDTO:
        entity = await self._repository.find_by_id(client_id)
        if entity is None:
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    @cache(
        namespace=CacheConstants.CLIENTS,
        expire=CacheConstants.SHORT_TTL,
        key_builder=page_key_builder,
    )
    async def find_all(self, page_request: PageRequest) -> PageResponse[ClientResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def update(self, client_id: UUID, dto: ClientRequestDTO) -> ClientResponseDTO:
        entity = await self._repository.find_by_id(client_id)
        if entity is None:
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        entity.corporate_name = dto.corporate_name
        entity.trade_name = dto.trade_name
        entity.email = dto.email
        entity.phone = dto.phone
        entity.address = dto.address
        entity.city = dto.city
        entity.state = dto.state
        entity.zip_code = dto.zip_code
        entity.active = dto.active
        entity.update_timestamp()
        saved = await self._repository.save(entity)
        await invalidate_cache(CacheConstants.CLIENTS)
        return self._mapper.to_response_dto(saved)

    async def delete(self, client_id: UUID) -> None:
        if not await self._repository.exists_by_id(client_id):
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        await self._repository.delete_by_id(client_id)
        await invalidate_cache(CacheConstants.CLIENTS)
