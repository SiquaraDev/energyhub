"""Repositório de persistência de `Payment`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.financial.domain.entity.payment import Payment
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class PaymentRepository(SQLAlchemyRepository[Payment, UUID]):
    """Repositório de `Payment`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Payment)

    async def find_by_invoice_id(self, invoice_id: UUID) -> list[Payment]:
        result = await self._session.execute(
            select(Payment).where(Payment.invoice_id == invoice_id)
        )
        return list(result.scalars().all())
