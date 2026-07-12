"""Repositório de persistência de `Permission`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.domain.entity.permission import Permission
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class PermissionRepository(SQLAlchemyRepository[Permission, UUID]):
    """Repositório de `Permission`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Permission)

    async def find_by_name(self, name: str) -> Permission | None:
        result = await self._session.execute(select(Permission).where(Permission.name == name))
        return result.scalar_one_or_none()

    async def exists_by_name(self, name: str) -> bool:
        result = await self._session.execute(select(exists().where(Permission.name == name)))
        return bool(result.scalar())
