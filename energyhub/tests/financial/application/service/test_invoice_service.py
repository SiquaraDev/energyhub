"""Testes unitários de `InvoiceService` (colaboradores mockados)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.financial.application.dto.invoice_request_dto import InvoiceRequestDTO
from energyhub.financial.application.service.invoice_service import InvoiceService
from energyhub.financial.domain.entity.invoice import Invoice
from energyhub.financial.domain.entity.invoice_status import InvoiceStatus
from energyhub.financial.domain.exception.invoice_already_exists_exception import (
    InvoiceAlreadyExistsException,
)
from energyhub.financial.domain.exception.invoice_not_found_exception import (
    InvoiceNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> InvoiceRequestDTO:
    data: dict[str, object] = {
        "invoice_number": "INV-2026-001",
        "client_id": uuid4(),
        "amount": Decimal("1500.00"),
        "due_date": date(2026, 2, 28),
        "status": InvoiceStatus.ISSUED,
    }
    data.update(overrides)
    return InvoiceRequestDTO(**data)


def _entity(**overrides: object) -> Invoice:
    data: dict[str, object] = {
        "invoice_number": "INV-2026-001",
        "client_id": uuid4(),
        "amount": Decimal("1500.00"),
        "due_date": date(2026, 2, 28),
        "status": InvoiceStatus.ISSUED,
    }
    data.update(overrides)
    return Invoice(**data)


async def test_should_create_invoice_when_number_is_unique() -> None:
    repo = AsyncMock()
    repo.exists_by_invoice_number.return_value = False
    repo.save.side_effect = lambda entity: entity

    service = InvoiceService(repo)
    response = await service.create(_request())

    assert response.invoice_number == "INV-2026-001"
    repo.save.assert_awaited_once()


async def test_should_raise_when_invoice_number_already_exists() -> None:
    repo = AsyncMock()
    repo.exists_by_invoice_number.return_value = True

    service = InvoiceService(repo)
    with pytest.raises(InvoiceAlreadyExistsException):
        await service.create(_request())

    repo.save.assert_not_awaited()


async def test_should_find_invoice_by_id() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=invoice_id)

    service = InvoiceService(repo)
    response = await service.find_by_id(invoice_id)

    assert response.id == invoice_id


async def test_should_raise_when_invoice_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = InvoiceService(repo)
    with pytest.raises(InvoiceNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_invoices_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = InvoiceService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_mark_invoice_as_paid_on_transition_to_paid() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=invoice_id, status=InvoiceStatus.ISSUED)
    repo.save.side_effect = lambda entity: entity

    service = InvoiceService(repo)
    response = await service.update(invoice_id, _request(status=InvoiceStatus.PAID))

    assert response.status == InvoiceStatus.PAID
    repo.save.assert_awaited_once()


async def test_should_update_invoice_without_paid_transition() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=invoice_id, status=InvoiceStatus.ISSUED)
    repo.save.side_effect = lambda entity: entity

    service = InvoiceService(repo)
    response = await service.update(
        invoice_id, _request(amount=Decimal("2000.00"), status=InvoiceStatus.OVERDUE)
    )

    assert response.amount == Decimal("2000.00")
    assert response.status == InvoiceStatus.OVERDUE


async def test_should_raise_when_updating_missing_invoice() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = InvoiceService(repo)
    with pytest.raises(InvoiceNotFoundException):
        await service.update(uuid4(), _request())


async def test_should_delete_invoice_when_it_exists() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = InvoiceService(repo)
    await service.delete(invoice_id)

    repo.delete_by_id.assert_awaited_once_with(invoice_id)


async def test_should_raise_when_deleting_missing_invoice() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = InvoiceService(repo)
    with pytest.raises(InvoiceNotFoundException):
        await service.delete(uuid4())
