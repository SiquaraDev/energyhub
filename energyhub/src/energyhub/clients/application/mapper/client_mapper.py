"""Mapper entre entidades de `clients` e seus DTOs."""

from __future__ import annotations

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.domain.entity.client import Client


class ClientMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Client`."""

    @staticmethod
    def to_entity(dto: ClientRequestDTO) -> Client:
        """Constrói um `Client` a partir do request DTO (id/timestamps gerados na persistência)."""
        return Client(
            cnpj=dto.cnpj,
            corporate_name=dto.corporate_name,
            trade_name=dto.trade_name,
            email=dto.email,
            phone=dto.phone,
            address=dto.address,
            city=dto.city,
            state=dto.state,
            zip_code=dto.zip_code,
            active=dto.active,
        )

    @staticmethod
    def to_response_dto(entity: Client) -> ClientResponseDTO:
        """Constrói o response DTO da entidade (contatos aninhados via from_attributes/selectin)."""
        return ClientResponseDTO.model_validate(entity)
