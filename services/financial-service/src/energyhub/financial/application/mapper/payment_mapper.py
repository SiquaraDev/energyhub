"""Mapper entre a entidade `Payment` e seus DTOs."""

from __future__ import annotations

from uuid import UUID

from energyhub.financial.application.dto.payment_request_dto import PaymentRequestDTO
from energyhub.financial.application.dto.payment_response_dto import PaymentResponseDTO
from energyhub.financial.domain.entity.payment import Payment


class PaymentMapper:
    """Ponto único de tradução entidade↔DTO para `Payment`."""

    @staticmethod
    def to_entity(invoice_id: UUID, dto: PaymentRequestDTO) -> Payment:
        """Constrói um `Payment` associado a `invoice_id` (do path) a partir do request DTO."""
        return Payment(
            invoice_id=invoice_id,
            amount=dto.amount,
            payment_date=dto.payment_date,
        )

    @staticmethod
    def to_response_dto(entity: Payment) -> PaymentResponseDTO:
        """Constrói o response DTO a partir da entidade."""
        return PaymentResponseDTO.model_validate(entity)
