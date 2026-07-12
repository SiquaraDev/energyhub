"""Repositório de persistência de `Negotiation`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.negotiations.domain.entity.negotiation import Negotiation
from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class NegotiationRepository(SQLAlchemyRepository[Negotiation, UUID]):
    """Repositório de `Negotiation`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Negotiation)

    async def find_by_contract_id(self, contract_id: UUID) -> list[Negotiation]:
        result = await self._session.execute(
            select(Negotiation).where(Negotiation.contract_id == contract_id)
        )
        return list(result.scalars().all())

    async def find_by_status(self, status: NegotiationStatus) -> list[Negotiation]:
        result = await self._session.execute(
            select(Negotiation).where(Negotiation.status == status)
        )
        return list(result.scalars().all())
