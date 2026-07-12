"""DTO de request de contrato."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.shared.application.validation.validators import validate_non_empty


class ContractRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar um contrato de energia."""

    contract_number: str = Field(..., description="Número do contrato")
    client_id: UUID = Field(..., description="Identificador do cliente")
    start_date: date = Field(..., description="Data de início da vigência")
    end_date: date = Field(..., description="Data de término da vigência")
    energy_amount: Decimal = Field(..., description="Quantidade de energia (MWh)")
    unit_price: Decimal = Field(..., description="Preço unitário")
    total_value: Decimal = Field(..., description="Valor total do contrato")
    type: ContractType = Field(..., description="Tipo do contrato")
    status: ContractStatus = Field(ContractStatus.DRAFT, description="Status do contrato")

    @field_validator("contract_number")
    @classmethod
    def _validate_contract_number(cls, value: str) -> str:
        return validate_non_empty(value)
