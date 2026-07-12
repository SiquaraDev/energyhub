"""DTO de request de negociação."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus


class NegotiationRequestDTO(BaseModel):
    """Dados de entrada para criar/atualizar uma negociação."""

    contract_id: UUID = Field(..., description="Id do contrato ao qual a negociação pertence")
    status: NegotiationStatus = Field(
        NegotiationStatus.DRAFT, description="Status da negociação (DRAFT, IN_PROGRESS, ...)"
    )
