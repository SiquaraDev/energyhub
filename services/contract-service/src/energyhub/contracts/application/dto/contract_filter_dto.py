"""DTO de filtro (critérios opcionais) para busca de `Contract`."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType


class ContractFilterDTO(BaseModel):
    """Critérios opcionais de filtragem de contratos (campos não informados são ignorados)."""

    contract_number: str | None = Field(
        None, description="Filtra pelo número do contrato", examples=["CT-2026-000123"]
    )
    client_id: UUID | None = Field(
        None,
        description="Filtra pelos contratos de um cliente",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    status: ContractStatus | None = Field(
        None, description="Filtra pelo status do contrato", examples=["ACTIVE"]
    )
    type: ContractType | None = Field(
        None, description="Filtra pelo tipo do contrato", examples=["PURCHASE"]
    )
    active_from: date | None = Field(
        None, description="Contratos vigentes a partir desta data", examples=["2026-01-01"]
    )
    active_to: date | None = Field(
        None, description="Contratos vigentes até esta data", examples=["2026-12-31"]
    )
    expiring_before: date | None = Field(
        None, description="Contratos que expiram antes desta data", examples=["2026-06-30"]
    )
