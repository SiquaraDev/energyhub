"""Testes unitários de `PaymentService` (colaboradores mockados)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.financial.application.dto.payment_request_dto import PaymentRequestDTO
from energyhub.financial.application.service.payment_service import PaymentService
from energyhub.financial.domain.entity.payment import Payment
from energyhub.financial.domain.exception.payment_not_found_exception import (
    PaymentNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request() -> PaymentRequestDTO:
    return PaymentRequestDTO(
        amount=Decimal("500.00"), payment_date=datetime(2026, 1, 15, tzinfo=timezone.utc)
    )


async def test_should_create_payment_bound_to_invoice() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = PaymentService(repo)
    response = await service.create(invoice_id, _request())

    assert response.invoice_id == invoice_id
    assert response.amount == Decimal("500.00")
    repo.save.assert_awaited_once()
    saved = repo.save.await_args.args[0]
    assert isinstance(saved, Payment)


async def test_should_find_payment_by_id() -> None:
    payment_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Payment(
        id=payment_id,
        invoice_id=uuid4(),
        amount=Decimal("500.00"),
        payment_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
    )

    service = PaymentService(repo)
    response = await service.find_by_id(payment_id)

    assert response.id == payment_id


async def test_should_raise_when_payment_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = PaymentService(repo)
    with pytest.raises(PaymentNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_payments_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = (
        [
            Payment(
                invoice_id=uuid4(),
                amount=Decimal("500.00"),
                payment_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
            )
        ],
        1,
    )

    service = PaymentService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_list_payments_by_invoice_id() -> None:
    invoice_id = uuid4()
    repo = AsyncMock()
    repo.find_by_invoice_id.return_value = [
        Payment(
            invoice_id=invoice_id,
            amount=Decimal("500.00"),
            payment_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
        )
    ]

    service = PaymentService(repo)
    result = await service.find_by_invoice_id(invoice_id)

    assert len(result) == 1
    assert result[0].invoice_id == invoice_id
    repo.find_by_invoice_id.assert_awaited_once_with(invoice_id)
