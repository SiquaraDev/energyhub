"""DTO de resposta de fatura."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.shared.application.dto.base_dto import BaseDTO


class InvoiceResponseDTO(BaseDTO):
    """Representação de saída de uma fatura (inclui id/timestamps do `BaseDTO`)."""

    invoice_number: str
    client_id: UUID
    amount: Decimal
    due_date: date
    status: InvoiceStatus
