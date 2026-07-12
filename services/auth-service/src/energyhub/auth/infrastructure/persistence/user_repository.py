"""Repositório de persistência de `User`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class UserRepository(SQLAlchemyRepository[User, UUID]):
    """Repositório de `User` com finders de autenticação."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def find_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def exists_by_username(self, username: str) -> bool:
        result = await self._session.execute(select(exists().where(User.username == username)))
        return bool(result.scalar())

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(select(exists().where(User.email == email)))
        return bool(result.scalar())

    async def find_by_role_name(self, role_name: str) -> list[User]:
        result = await self._session.execute(
            select(User).join(User.roles).where(Role.name == role_name)
        )
        return list(result.scalars().unique().all())
