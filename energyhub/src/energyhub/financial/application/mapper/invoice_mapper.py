"""Mapper entre a entidade `Invoice` e seus DTOs."""

from __future__ import annotations

from energyhub.financial.application.dto.invoice_request_dto import InvoiceRequestDTO
from energyhub.financial.application.dto.invoice_response_dto import InvoiceResponseDTO
from energyhub.financial.domain.entity.invoice import Invoice


class InvoiceMapper:
    """Ponto único de tradução entidade↔DTO para o agregado `Invoice`."""

    @staticmethod
    def to_entity(dto: InvoiceRequestDTO) -> Invoice:
        """Constrói uma `Invoice` a partir do request DTO (FK como campo, sem relação ORM)."""
        return Invoice(
            invoice_number=dto.invoice_number,
            client_id=dto.client_id,
            amount=dto.amount,
            due_date=dto.due_date,
            status=dto.status,
        )

    @staticmethod
    def to_response_dto(entity: Invoice) -> InvoiceResponseDTO:
        """Constrói o response DTO a partir da entidade."""
        return InvoiceResponseDTO.model_validate(entity)
