"""Testes unitários de `EnergyTransactionService` (colaboradores mockados)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.negotiations.application.dto.energy_transaction_request_dto import (
    EnergyTransactionRequestDTO,
)
from energyhub.negotiations.application.service.energy_transaction_service import (
    EnergyTransactionService,
)
from energyhub.negotiations.domain.entity.energy_transaction import EnergyTransaction
from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.negotiations.domain.exception.energy_transaction_not_found_exception import (
    EnergyTransactionNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request() -> EnergyTransactionRequestDTO:
    return EnergyTransactionRequestDTO(
        amount=Decimal("10.5"),
        price=Decimal("300.00"),
        type=TransactionType.BUY,
        transaction_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
    )


def _entity(**overrides: object) -> EnergyTransaction:
    data: dict[str, object] = {
        "negotiation_id": uuid4(),
        "amount": Decimal("10.5"),
        "price": Decimal("300.00"),
        "type": TransactionType.BUY,
        "transaction_date": datetime(2026, 1, 10, tzinfo=timezone.utc),
    }
    data.update(overrides)
    return EnergyTransaction(**data)


async def test_should_create_transaction_bound_to_negotiation() -> None:
    negotiation_id = uuid4()
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = EnergyTransactionService(repo)
    response = await service.create(negotiation_id, _request())

    assert response.negotiation_id == negotiation_id
    assert response.type == TransactionType.BUY
    repo.save.assert_awaited_once()


async def test_should_find_transaction_by_id() -> None:
    transaction_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=transaction_id)

    service = EnergyTransactionService(repo)
    response = await service.find_by_id(transaction_id)

    assert response.id == transaction_id


async def test_should_raise_when_transaction_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = EnergyTransactionService(repo)
    with pytest.raises(EnergyTransactionNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_transactions_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = EnergyTransactionService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_list_transactions_by_negotiation_id() -> None:
    negotiation_id = uuid4()
    repo = AsyncMock()
    repo.find_by_negotiation_id.return_value = [_entity(negotiation_id=negotiation_id)]

    service = EnergyTransactionService(repo)
    result = await service.find_by_negotiation_id(negotiation_id)

    assert len(result) == 1
    assert result[0].negotiation_id == negotiation_id
    repo.find_by_negotiation_id.assert_awaited_once_with(negotiation_id)
