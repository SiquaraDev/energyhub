"""Mapper entre a entidade `EnergyTransaction` e seus DTOs."""

from __future__ import annotations

from uuid import UUID

from energyhub.negotiations.application.dto.energy_transaction_request_dto import (
    EnergyTransactionRequestDTO,
)
from energyhub.negotiations.application.dto.energy_transaction_response_dto import (
    EnergyTransactionResponseDTO,
)
from energyhub.negotiations.domain.entity.energy_transaction import EnergyTransaction


class EnergyTransactionMapper:
    """Ponto único de tradução entidade↔DTO para `EnergyTransaction`."""

    @staticmethod
    def to_entity(negotiation_id: UUID, dto: EnergyTransactionRequestDTO) -> EnergyTransaction:
        """Constrói uma `EnergyTransaction` associada a `negotiation_id` (do path)."""
        return EnergyTransaction(
            negotiation_id=negotiation_id,
            amount=dto.amount,
            price=dto.price,
            type=dto.type,
            transaction_date=dto.transaction_date,
        )

    @staticmethod
    def to_response_dto(entity: EnergyTransaction) -> EnergyTransactionResponseDTO:
        """Constrói o response DTO a partir da entidade."""
        return EnergyTransactionResponseDTO.model_validate(entity)
