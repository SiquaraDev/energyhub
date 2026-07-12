"""Repositório de persistência de `EnergyTransaction`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.negotiations.domain.entity.energy_transaction import EnergyTransaction
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class EnergyTransactionRepository(SQLAlchemyRepository[EnergyTransaction, UUID]):
    """Repositório de `EnergyTransaction`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, EnergyTransaction)

    async def find_by_negotiation_id(self, negotiation_id: UUID) -> list[EnergyTransaction]:
        result = await self._session.execute(
            select(EnergyTransaction).where(EnergyTransaction.negotiation_id == negotiation_id)
        )
        return list(result.scalars().all())
