"""DTO de resposta de negociação."""

from __future__ import annotations

from uuid import UUID

from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class NegotiationResponseDTO(BaseDTO):
    """Representação de saída de uma negociação (inclui id/timestamps do `BaseDTO`)."""

    contract_id: UUID
    status: NegotiationStatus
