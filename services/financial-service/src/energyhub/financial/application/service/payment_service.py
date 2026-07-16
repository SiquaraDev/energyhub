"""Serviço de aplicação de pagamentos (sub-recurso de fatura)."""

from __future__ import annotations

from uuid import UUID

from energyhub.financial.application.dto.payment_request_dto import PaymentRequestDTO
from energyhub.financial.application.dto.payment_response_dto import PaymentResponseDTO
from energyhub.financial.application.mapper.payment_mapper import PaymentMapper
from energyhub.financial.domain.exception.payment_not_found_exception import (
    PaymentNotFoundException,
)
from energyhub.financial.infrastructure.persistence.payment_repository import PaymentRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.infrastructure.messaging.audit_event import AuditEvent
from energyhub.shared.infrastructure.messaging.audit_event_producer import audit_event_producer
from energyhub.shared.infrastructure.messaging.publish_helper import publish_safely
from energyhub.shared.infrastructure.security.actor_context import get_current_actor


class PaymentService:
    """Cria/lista pagamentos. Persiste via FK (`PaymentRepository`), sem checagem de unicidade."""

    def __init__(self, repository: PaymentRepository, mapper: PaymentMapper | None = None) -> None:
        self._repository = repository
        self._mapper = mapper or PaymentMapper()

    async def create(self, invoice_id: UUID, dto: PaymentRequestDTO) -> PaymentResponseDTO:
        entity = self._mapper.to_entity(invoice_id, dto)
        saved = await self._repository.save(entity)
        response = self._mapper.to_response_dto(saved)
        await publish_safely(
            audit_event_producer.publish_audit(
                AuditEvent(
                    user_id=get_current_actor(),
                    action="CREATE",  # CREATE | UPDATE | DELETE — valores do enum AuditAction
                    entity_type="Payment",
                    entity_id=response.id,
                    details={"invoice_id": str(response.invoice_id)},
                )
            ),
            event="audit",
        )
        return response

    async def find_by_id(self, payment_id: UUID) -> PaymentResponseDTO:
        entity = await self._repository.find_by_id(payment_id)
        if entity is None:
            raise PaymentNotFoundException(f"Pagamento {payment_id} não encontrado")
        return self._mapper.to_response_dto(entity)

    async def find_all(self, page_request: PageRequest) -> PageResponse[PaymentResponseDTO]:
        content, total = await self._repository.find_page(
            page_request.get_offset(), page_request.get_limit()
        )
        dtos = [self._mapper.to_response_dto(entity) for entity in content]
        return PageResponse.create(dtos, page_request.page, page_request.size, total)

    async def find_by_invoice_id(self, invoice_id: UUID) -> list[PaymentResponseDTO]:
        payments = await self._repository.find_by_invoice_id(invoice_id)
        return [self._mapper.to_response_dto(payment) for payment in payments]
