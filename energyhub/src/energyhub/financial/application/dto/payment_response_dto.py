"""DTO de resposta de pagamento."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from energyhub.shared.application.dto.base_dto import BaseDTO


class PaymentResponseDTO(BaseDTO):
    """Representação de saída de um pagamento (inclui id/timestamps do `BaseDTO`)."""

    invoice_id: UUID
    amount: Decimal
    payment_date: datetime
