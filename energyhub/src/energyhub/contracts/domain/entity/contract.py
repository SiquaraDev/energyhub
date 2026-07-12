from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.contracts.domain.exception.invalid_contract_status_exception import (
    InvalidContractStatusException,
)
from energyhub.shared.domain.entity.base_entity import BaseEntity
from energyhub.shared.domain.exception.validation_exception import ValidationException

if TYPE_CHECKING:
    from energyhub.clients.domain.entity.client import Client


@dataclass(kw_only=True, eq=False)
class Contract(BaseEntity):
    """Contrato de energia (raiz do ContractAggregate)."""

    contract_number: str
    client_id: UUID
    start_date: date
    end_date: date
    energy_amount: Decimal
    unit_price: Decimal
    total_value: Decimal
    type: ContractType
    status: ContractStatus = ContractStatus.DRAFT
    client: Client | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.contract_number or not self.contract_number.strip():
            raise ValidationException("contract_number não pode ser vazio")
        if self.end_date <= self.start_date:
            raise ValidationException("end_date deve ser posterior a start_date")
        if self.energy_amount <= Decimal(0):
            raise ValidationException("energy_amount deve ser positivo")
        if self.unit_price <= Decimal(0):
            raise ValidationException("unit_price deve ser positivo")
        if self.total_value <= Decimal(0):
            raise ValidationException("total_value deve ser positivo")

    def approve(self) -> None:
        """Aprova o contrato (exige status PENDING_APPROVAL)."""
        if self.status != ContractStatus.PENDING_APPROVAL:
            raise InvalidContractStatusException(
                f"não é possível aprovar contrato no status {self.status.value}"
            )
        self.status = ContractStatus.APPROVED
        self.update_timestamp()

    def activate(self) -> None:
        """Ativa o contrato (exige status APPROVED e start_date não futura)."""
        if self.status != ContractStatus.APPROVED:
            raise InvalidContractStatusException(
                f"não é possível ativar contrato no status {self.status.value}"
            )
        if self.start_date > date.today():
            raise InvalidContractStatusException("start_date no futuro")
        self.status = ContractStatus.ACTIVE
        self.update_timestamp()
