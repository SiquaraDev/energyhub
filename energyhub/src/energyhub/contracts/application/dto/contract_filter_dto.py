"""DTO de filtro (critérios opcionais) para busca de `Contract`."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from pydantic import BaseModel

from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType


class ContractFilterDTO(BaseModel):
    """Critérios opcionais de filtragem de contratos (campos não informados são ignorados)."""

    contract_number: str | None = None
    client_id: UUID | None = None
    status: ContractStatus | None = None
    type: ContractType | None = None
    active_from: date | None = None
    active_to: date | None = None
    expiring_before: date | None = None
