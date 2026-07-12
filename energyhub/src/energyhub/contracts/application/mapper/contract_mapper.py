"""Mapper entre entidades de `contracts` e seus DTOs."""

from __future__ import annotations

from energyhub.contracts.application.dto.contract_request_dto import ContractRequestDTO
from energyhub.contracts.application.dto.contract_response_dto import ContractResponseDTO
from energyhub.contracts.domain.entity.contract import Contract


class ContractMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Contract`."""

    @staticmethod
    def to_entity(dto: ContractRequestDTO) -> Contract:
        """Constrói um `Contract` a partir do request DTO (id/timestamps na persistência)."""
        return Contract(
            contract_number=dto.contract_number,
            client_id=dto.client_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
            energy_amount=dto.energy_amount,
            unit_price=dto.unit_price,
            total_value=dto.total_value,
            type=dto.type,
            status=dto.status,
        )

    @staticmethod
    def to_response_dto(entity: Contract) -> ContractResponseDTO:
        """Constrói o response DTO da entidade (campos escalares + FK via from_attributes)."""
        return ContractResponseDTO.model_validate(entity)
