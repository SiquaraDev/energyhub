"""Repositório de persistência de `Notification`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.notifications.domain.entity.notification import Notification
from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class NotificationRepository(SQLAlchemyRepository[Notification, UUID]):
    """Repositório de `Notification`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Notification)

    async def find_by_user_id(self, user_id: UUID) -> list[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.user_id == user_id)
        )
        return list(result.scalars().all())

    async def find_by_status(self, status: NotificationStatus) -> list[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.status == status)
        )
        return list(result.scalars().all())
