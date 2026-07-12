"""DTO de resposta de contrato."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.shared.application.dto.base_dto import BaseDTO


class ContractResponseDTO(BaseDTO):
    """Representação de saída de um contrato (inclui id/timestamps do `BaseDTO`)."""

    contract_number: str
    client_id: UUID
    start_date: date
    end_date: date
    energy_amount: Decimal
    unit_price: Decimal
    total_value: Decimal
    type: ContractType
    status: ContractStatus = ContractStatus.DRAFT
