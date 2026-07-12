"""Testes de componente do `FinancialRouter` (faturas + pagamentos; serviços mockados)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.financial.application.dto.invoice_response_dto import InvoiceResponseDTO
from energyhub.financial.application.dto.payment_response_dto import PaymentResponseDTO
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.financial.presentation.router.financial_router import (
    FinancialRouter,
    get_create_invoice_use_case,
    get_invoice_service,
    get_payment_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _invoice_dto() -> InvoiceResponseDTO:
    return InvoiceResponseDTO(
        id=uuid4(),
        invoice_number="INV-2026-001",
        client_id=uuid4(),
        amount=Decimal("1500.00"),
        due_date=date(2026, 2, 28),
        status=InvoiceStatus.ISSUED,
    )


def _payment_dto(invoice_id: Any) -> PaymentResponseDTO:
    return PaymentResponseDTO(
        id=uuid4(),
        invoice_id=invoice_id,
        amount=Decimal("500.00"),
        payment_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )


def _invoice_payload() -> dict[str, Any]:
    return {
        "invoice_number": "INV-2026-001",
        "client_id": str(uuid4()),
        "amount": "1500.00",
        "due_date": "2026-02-28",
    }


def test_create_invoice_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _invoice_dto()
    api = router_client(
        FinancialRouter().get_router(), {get_create_invoice_use_case: lambda: use_case}
    )

    response = api.post("/api/v1/invoices", json=_invoice_payload())

    assert response.status_code == 201
    assert response.json()["invoice_number"] == "INV-2026-001"


def test_get_invoice_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _invoice_dto()
    api = router_client(FinancialRouter().get_router(), {get_invoice_service: lambda: service})

    response = api.get(f"/api/v1/invoices/{uuid4()}")

    assert response.status_code == 200


def test_list_invoices_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_invoice_dto()], 0, 20, 1)
    api = router_client(FinancialRouter().get_router(), {get_invoice_service: lambda: service})

    response = api.get("/api/v1/invoices")

    assert response.status_code == 200


def test_update_invoice_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _invoice_dto()
    api = router_client(FinancialRouter().get_router(), {get_invoice_service: lambda: service})

    response = api.put(f"/api/v1/invoices/{uuid4()}", json=_invoice_payload())

    assert response.status_code == 200


def test_delete_invoice_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(FinancialRouter().get_router(), {get_invoice_service: lambda: service})

    response = api.delete(f"/api/v1/invoices/{uuid4()}")

    assert response.status_code == 204


def test_add_payment_returns_201(router_client: Any) -> None:
    invoice_id = uuid4()
    service = AsyncMock()
    service.create.return_value = _payment_dto(invoice_id)
    api = router_client(FinancialRouter().get_router(), {get_payment_service: lambda: service})

    response = api.post(
        f"/api/v1/invoices/{invoice_id}/payments",
        json={"amount": "500.00", "payment_date": "2026-01-15T00:00:00Z"},
    )

    assert response.status_code == 201


def test_list_payments_returns_200(router_client: Any) -> None:
    invoice_id = uuid4()
    service = AsyncMock()
    service.find_by_invoice_id.return_value = [_payment_dto(invoice_id)]
    api = router_client(FinancialRouter().get_router(), {get_payment_service: lambda: service})

    response = api.get(f"/api/v1/invoices/{invoice_id}/payments")

    assert response.status_code == 200
    assert len(response.json()) == 1
