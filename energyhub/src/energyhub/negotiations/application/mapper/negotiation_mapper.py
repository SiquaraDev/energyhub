"""Mapper entre a entidade `Negotiation` e seus DTOs."""

from __future__ import annotations

from energyhub.negotiations.application.dto.negotiation_request_dto import NegotiationRequestDTO
from energyhub.negotiations.application.dto.negotiation_response_dto import NegotiationResponseDTO
from energyhub.negotiations.domain.entity.negotiation import Negotiation


class NegotiationMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Negotiation`."""

    @staticmethod
    def to_entity(dto: NegotiationRequestDTO) -> Negotiation:
        """Constrói uma `Negotiation` a partir do request DTO (id/timestamps na persistência)."""
        return Negotiation(
            contract_id=dto.contract_id,
            status=dto.status,
        )

    @staticmethod
    def to_response_dto(entity: Negotiation) -> NegotiationResponseDTO:
        """Constrói o response DTO a partir da entidade."""
        return NegotiationResponseDTO.model_validate(entity)
