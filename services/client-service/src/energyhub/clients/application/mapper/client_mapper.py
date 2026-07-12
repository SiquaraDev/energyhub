"""Mapper entre entidades de `clients` e seus DTOs."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.domain.entity.client import Client

if TYPE_CHECKING:
    from energyhub.clients.infrastructure.search.client_document import ClientDocument


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

    @staticmethod
    def document_to_response_dto(document: ClientDocument) -> ClientResponseDTO:
        """Constrói o response DTO a partir de um documento de busca (Fase 11).

        O id vem de `meta.id`; campos não indexados (ausentes na projeção) caem para o default.
        """
        return ClientResponseDTO(
            id=UUID(document.meta.id),
            cnpj=document.cnpj,
            corporate_name=document.corporate_name,
            trade_name=getattr(document, "trade_name", None),
            email=getattr(document, "email", None),
            phone=getattr(document, "phone", None),
            address=getattr(document, "address", None),
            city=getattr(document, "city", None),
            state=getattr(document, "state", None),
            zip_code=getattr(document, "zip_code", None),
            active=bool(getattr(document, "active", True)),
            created_at=getattr(document, "created_at", None),
            updated_at=getattr(document, "updated_at", None),
        )
