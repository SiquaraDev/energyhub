"""Repositório de persistência de `Role`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.domain.entity.role import Role
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class RoleRepository(SQLAlchemyRepository[Role, UUID]):
    """Repositório de `Role`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Role)

    async def find_by_name(self, name: str) -> Role | None:
        result = await self._session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        result = await self._session.execute(select(exists().where(Role.name == name)))
        return bool(result.scalar())
