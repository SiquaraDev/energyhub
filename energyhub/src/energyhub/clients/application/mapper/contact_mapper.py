"""Mapper entre `Contact` e seus DTOs."""

from __future__ import annotations

from uuid import UUID

from energyhub.clients.application.dto.contact_request_dto import ContactRequestDTO
from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.clients.domain.entity.contact import Contact


class ContactMapper:
    """Ponto único de tradução entidade↔DTO para `Contact`."""

    @staticmethod
    def to_entity(client_id: UUID, dto: ContactRequestDTO) -> Contact:
        """Constrói um `Contact` associado a `client_id` a partir do request DTO."""
        return Contact(
            client_id=client_id,
            name=dto.name,
            type=dto.type,
            email=dto.email,
            phone=dto.phone,
            position=dto.position,
        )

    @staticmethod
    def to_response_dto(entity: Contact) -> ContactResponseDTO:
        """Constrói o response DTO a partir da entidade."""
        return ContactResponseDTO.model_validate(entity)
