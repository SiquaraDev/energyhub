"""DTO de resposta de contrato."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.shared.application.dto.base_dto import BaseDTO


class ContractResponseDTO(BaseDTO):
    """Representação de saída de um contrato (inclui id/timestamps do `BaseDTO`)."""

    contract_number: str = Field(
        ..., description="Número identificador do contrato", examples=["CT-2026-000123"]
    )
    client_id: UUID = Field(
        ...,
        description="Identificador do cliente vinculado ao contrato",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    start_date: date = Field(
        ..., description="Data de início da vigência do contrato", examples=["2026-01-01"]
    )
    end_date: date = Field(
        ..., description="Data de término da vigência do contrato", examples=["2026-12-31"]
    )
    energy_amount: Decimal = Field(
        ..., description="Quantidade de energia contratada em MWh", examples=["1500.00"]
    )
    unit_price: Decimal = Field(..., description="Preço unitário da energia", examples=["250.00"])
    total_value: Decimal = Field(..., description="Valor total do contrato", examples=["375000.00"])
    type: ContractType = Field(..., description="Tipo do contrato", examples=["PURCHASE"])
    status: ContractStatus = Field(
        ContractStatus.DRAFT, description="Status do contrato no ciclo de vida", examples=["DRAFT"]
    )
