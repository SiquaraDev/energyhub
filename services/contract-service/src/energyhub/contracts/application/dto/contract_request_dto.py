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

    contract_number: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Número identificador do contrato (não pode ser vazio)",
        examples=["CT-2026-000123"],
    )
    client_id: UUID = Field(
        ...,
        description="Identificador do cliente vinculado ao contrato",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    start_date: date = Field(
        ...,
        description="Data de início da vigência do contrato",
        examples=["2026-01-01"],
    )
    end_date: date = Field(
        ...,
        description="Data de término da vigência (deve ser posterior à data de início)",
        examples=["2026-12-31"],
    )
    energy_amount: Decimal = Field(
        ...,
        gt=0,
        description="Quantidade de energia contratada em MWh (deve ser positiva)",
        examples=["1500.00"],
    )
    unit_price: Decimal = Field(
        ...,
        gt=0,
        description="Preço unitário da energia (deve ser positivo)",
        examples=["250.00"],
    )
    total_value: Decimal = Field(
        ...,
        gt=0,
        description="Valor total do contrato (deve ser positivo)",
        examples=["375000.00"],
    )
    type: ContractType = Field(
        ...,
        description="Tipo do contrato (compra, venda ou bidirecional)",
        examples=["PURCHASE"],
    )
    status: ContractStatus = Field(
        ContractStatus.DRAFT,
        description="Status do contrato no ciclo de vida",
        examples=["DRAFT"],
    )

    @field_validator("contract_number")
    @classmethod
    def _validate_contract_number(cls, value: str) -> str:
        return validate_non_empty(value)
