"""Repositório de persistência de `AuditLog`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class AuditLogRepository(SQLAlchemyRepository[AuditLog, UUID]):
    """Repositório de `AuditLog`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)

    async def find_by_user_id(self, user_id: UUID) -> list[AuditLog]:
        result = await self._session.execute(select(AuditLog).where(AuditLog.user_id == user_id))
        return list(result.scalars().all())

    async def find_by_entity_type(self, entity_type: str) -> list[AuditLog]:
        result = await self._session.execute(
            select(AuditLog).where(AuditLog.entity_type == entity_type)
        )
        return list(result.scalars().all())
