"""Repositório de persistência de `Contact`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class ContactRepository(SQLAlchemyRepository[Contact, UUID]):
    """Repositório de `Contact`."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Contact)

    async def find_by_client_id(self, client_id: UUID) -> list[Contact]:
        result = await self._session.execute(select(Contact).where(Contact.client_id == client_id))
        return list(result.scalars().all())

    async def find_by_client_id_and_type(
        self, client_id: UUID, contact_type: ContactType
    ) -> list[Contact]:
        result = await self._session.execute(
            select(Contact).where(Contact.client_id == client_id, Contact.type == contact_type)
        )
        return list(result.scalars().all())
