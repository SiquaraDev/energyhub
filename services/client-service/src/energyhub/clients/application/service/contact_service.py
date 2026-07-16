"""Serviço de aplicação para contatos (sub-recurso de cliente)."""

from __future__ import annotations

from uuid import UUID

from energyhub.clients.application.dto.contact_request_dto import ContactRequestDTO
from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.clients.application.mapper.contact_mapper import ContactMapper
from energyhub.clients.domain.exception.client_not_found_exception import ClientNotFoundException
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.clients.infrastructure.persistence.contact_repository import ContactRepository
from energyhub.shared.infrastructure.messaging.audit_event import AuditEvent
from energyhub.shared.infrastructure.messaging.audit_event_producer import audit_event_producer
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.security.actor_context import get_current_actor


class ContactService:
    """Cria/lista contatos de um cliente. Persiste via FK (`ContactRepository`), sem relação ORM."""

    def __init__(
        self,
        contact_repository: ContactRepository,
        client_repository: ClientRepository,
        mapper: ContactMapper | None = None,
    ) -> None:
        self._contacts = contact_repository
        self._clients = client_repository
        self._mapper = mapper or ContactMapper()

    async def create(self, client_id: UUID, dto: ContactRequestDTO) -> ContactResponseDTO:
        if not await self._clients.exists_by_id(client_id):
            raise ClientNotFoundException(f"Cliente {client_id} não encontrado")
        contact = self._mapper.to_entity(client_id, dto)
        saved = await self._contacts.save(contact)
        response = self._mapper.to_response_dto(saved)
        await publish_safely(
            audit_event_producer.publish_audit(
                AuditEvent(
                    user_id=get_current_actor(),
                    action="CREATE",  # CREATE | UPDATE | DELETE — valores do enum AuditAction
                    entity_type="Contact",
                    entity_id=response.id,
                    details={"name": response.name, "client_id": str(response.client_id)},
                )
            ),
            event="audit",
        )
        return response

    async def find_by_client_id(self, client_id: UUID) -> list[ContactResponseDTO]:
        contacts = await self._contacts.find_by_client_id(client_id)
        return [self._mapper.to_response_dto(contact) for contact in contacts]
