"""Repositório de persistência de `Contract`."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.contracts.application.dto.contract_filter_dto import ContractFilterDTO
from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.infrastructure.persistence.contract_filter import ContractFilter
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)


class ContractRepository(SQLAlchemyRepository[Contract, UUID]):
    """Repositório de `Contract` com finders de negócio."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Contract)

    async def find_by_contract_number(self, contract_number: str) -> Contract | None:
        result = await self._session.execute(
            select(Contract).where(Contract.contract_number == contract_number)
        )
        return result.scalar_one_or_none()

    async def exists_by_contract_number(self, contract_number: str) -> bool:
        result = await self._session.execute(
            select(exists().where(Contract.contract_number == contract_number))
        )
        return bool(result.scalar())

    async def find_by_client_id(self, client_id: UUID) -> list[Contract]:
        result = await self._session.execute(
            select(Contract).where(Contract.client_id == client_id)
        )
        return list(result.scalars().all())

    async def find_by_status(self, status: ContractStatus) -> list[Contract]:
        result = await self._session.execute(select(Contract).where(Contract.status == status))
        return list(result.scalars().all())

    async def search(self, criteria: ContractFilterDTO) -> list[Contract]:
        """Traduz os campos preenchidos do DTO em predicados e consulta (combinados por AND)."""
        conditions = []
        if criteria.contract_number is not None:
            conditions.append(ContractFilter.has_contract_number(criteria.contract_number))
        if criteria.client_id is not None:
            conditions.append(ContractFilter.has_client_id(criteria.client_id))
        if criteria.status is not None:
            conditions.append(ContractFilter.has_status(criteria.status))
        if criteria.type is not None:
            conditions.append(ContractFilter.has_type(criteria.type))
        if criteria.active_from is not None and criteria.active_to is not None:
            conditions.append(
                ContractFilter.is_active_between(criteria.active_from, criteria.active_to)
            )
        if criteria.expiring_before is not None:
            conditions.append(ContractFilter.expiring_before(criteria.expiring_before))
        return await self.find_by(*conditions)
