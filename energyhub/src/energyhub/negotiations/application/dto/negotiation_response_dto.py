"""DTO de resposta de negociação."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class NegotiationResponseDTO(BaseDTO):
    """Representação de saída de uma negociação (inclui id/timestamps do `BaseDTO`)."""

    contract_id: UUID = Field(
        ...,
        description="Id do contrato ao qual a negociação pertence",
        examples=["0b1e5b2e-6c3a-4e2a-9f1a-2b3c4d5e6f70"],
    )
    status: NegotiationStatus = Field(
        ...,
        description="Status atual da negociação (DRAFT, IN_PROGRESS, ...)",
        examples=["DRAFT"],
    )
