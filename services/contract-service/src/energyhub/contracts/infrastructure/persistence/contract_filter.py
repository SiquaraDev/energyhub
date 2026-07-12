"""Predicados componíveis de consulta para `Contract` (construtores de condição SQLAlchemy)."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.sql.elements import ColumnElement

from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType


class ContractFilter:
    """Cada método retorna uma condição SQLAlchemy; combine-as via `and_`/`or_` no repositório."""

    @staticmethod
    def has_contract_number(contract_number: str) -> ColumnElement[bool]:
        return Contract.contract_number == contract_number

    @staticmethod
    def has_client_id(client_id: UUID) -> ColumnElement[bool]:
        return Contract.client_id == client_id

    @staticmethod
    def has_status(status: ContractStatus) -> ColumnElement[bool]:
        return Contract.status == status

    @staticmethod
    def has_type(contract_type: ContractType) -> ColumnElement[bool]:
        return Contract.type == contract_type

    @staticmethod
    def is_active_between(start: date, end: date) -> ColumnElement[bool]:
        """Contratos vigentes em toda a janela `[start, end]`."""
        return and_(Contract.start_date <= start, Contract.end_date >= end)

    @staticmethod
    def expiring_before(reference: date) -> ColumnElement[bool]:
        return Contract.end_date < reference
