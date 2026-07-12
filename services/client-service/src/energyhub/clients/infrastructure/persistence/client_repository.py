"""Repositório de persistência de `Client`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.clients.application.dto.client_filter_dto import ClientFilterDTO
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.infrastructure.persistence.client_filter import ClientFilter
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class ClientRepository(SQLAlchemyRepository[Client, UUID]):
    """Repositório de `Client` com finders de negócio."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Client)

    async def find_by_cnpj(self, cnpj: str) -> Client | None:
        result = await self._session.execute(select(Client).where(Client.cnpj == cnpj))
        return result.scalar_one_or_none()

    async def exists_by_cnpj(self, cnpj: str) -> bool:
        result = await self._session.execute(select(exists().where(Client.cnpj == cnpj)))
        return bool(result.scalar())

    async def find_by_active_true(self) -> list[Client]:
        result = await self._session.execute(select(Client).where(Client.active.is_(True)))
        return list(result.scalars().all())

    async def search_by_name(self, name: str) -> list[Client]:
        pattern = f"%{name}%"
        result = await self._session.execute(
            select(Client).where(Client.corporate_name.ilike(pattern))
        )
        return list(result.scalars().all())

    async def find_by_location(
        self, city: str | None = None, state: str | None = None
    ) -> list[Client]:
        stmt = select(Client)
        if city is not None:
            stmt = stmt.where(Client.city == city)
        if state is not None:
            stmt = stmt.where(Client.state == state)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search(self, criteria: ClientFilterDTO) -> list[Client]:
        """Traduz os campos preenchidos do DTO em predicados e consulta (combinados por AND)."""
        conditions = []
        if criteria.cnpj is not None:
            conditions.append(ClientFilter.has_cnpj(criteria.cnpj))
        if criteria.corporate_name is not None:
            conditions.append(ClientFilter.has_corporate_name(criteria.corporate_name))
        if criteria.active is not None:
            conditions.append(ClientFilter.is_active(criteria.active))
        if criteria.city is not None:
            conditions.append(ClientFilter.has_city(criteria.city))
        if criteria.state is not None:
            conditions.append(ClientFilter.has_state(criteria.state))
        if criteria.contact_type is not None:
            conditions.append(ClientFilter.with_contact_type(criteria.contact_type))
        return await self.find_by(*conditions)
