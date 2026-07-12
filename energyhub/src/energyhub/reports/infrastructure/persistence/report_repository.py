"""Repositório de persistência de `Report`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.reports.domain.entity.report import Report
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class ReportRepository(SQLAlchemyRepository[Report, UUID]):
    """Repositório de `Report`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Report)

    async def find_by_generated_by(self, generated_by: UUID) -> list[Report]:
        result = await self._session.execute(
            select(Report).where(Report.generated_by == generated_by)
        )
        return list(result.scalars().all())
