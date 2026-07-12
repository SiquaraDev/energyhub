"""Repositório de persistência de `Invoice`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class InvoiceRepository(SQLAlchemyRepository[Invoice, UUID]):
    """Repositório de `Invoice` com finders de negócio."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Invoice)

    async def find_by_invoice_number(self, invoice_number: str) -> Invoice | None:
        result = await self._session.execute(
            select(Invoice).where(Invoice.invoice_number == invoice_number)
        )
        return result.scalar_one_or_none()

    async def exists_by_invoice_number(self, invoice_number: str) -> bool:
        result = await self._session.execute(
            select(exists().where(Invoice.invoice_number == invoice_number))
        )
        return bool(result.scalar())

    async def find_by_client_id(self, client_id: UUID) -> list[Invoice]:
        result = await self._session.execute(select(Invoice).where(Invoice.client_id == client_id))
        return list(result.scalars().all())

    async def find_by_status(self, status: InvoiceStatus) -> list[Invoice]:
        result = await self._session.execute(select(Invoice).where(Invoice.status == status))
        return list(result.scalars().all())
