"""Testes unitários de `ContractService` (colaboradores mockados)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.contracts.application.dto.contract_request_dto import ContractRequestDTO
from energyhub.contracts.application.service.contract_service import ContractService
from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.contracts.domain.exception.contract_already_exists_exception import (
    ContractAlreadyExistsException,
)
from energyhub.contracts.domain.exception.contract_not_found_exception import (
    ContractNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> ContractRequestDTO:
    data: dict[str, object] = {
        "contract_number": "CT-2026-001",
        "client_id": uuid4(),
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
        "energy_amount": Decimal("100.5"),
        "unit_price": Decimal("250.00"),
        "total_value": Decimal("25125.00"),
        "type": ContractType.PURCHASE,
        "status": ContractStatus.DRAFT,
    }
    data.update(overrides)
    return ContractRequestDTO(**data)


def _entity(**overrides: object) -> Contract:
    data: dict[str, object] = {
        "contract_number": "CT-2026-001",
        "client_id": uuid4(),
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
        "energy_amount": Decimal("100.5"),
        "unit_price": Decimal("250.00"),
        "total_value": Decimal("25125.00"),
        "type": ContractType.PURCHASE,
        "status": ContractStatus.DRAFT,
    }
    data.update(overrides)
    return Contract(**data)


async def test_should_create_contract_when_number_is_unique() -> None:
    repo = AsyncMock()
    repo.exists_by_contract_number.return_value = False
    repo.save.side_effect = lambda entity: entity

    service = ContractService(repo)
    response = await service.create(_request())

    assert response.contract_number == "CT-2026-001"
    repo.save.assert_awaited_once()


async def test_should_publish_to_kafka_when_producer_is_present() -> None:
    repo = AsyncMock()
    repo.exists_by_contract_number.return_value = False
    repo.save.side_effect = lambda entity: entity
    kafka = AsyncMock()

    service = ContractService(repo, kafka_producer=kafka)
    await service.create(_request())

    kafka.publish.assert_awaited_once()


async def test_should_raise_when_contract_number_already_exists() -> None:
    repo = AsyncMock()
    repo.exists_by_contract_number.return_value = True

    service = ContractService(repo)
    with pytest.raises(ContractAlreadyExistsException):
        await service.create(_request())

    repo.save.assert_not_awaited()


async def test_should_find_contract_by_id() -> None:
    contract_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=contract_id)

    service = ContractService(repo)
    response = await service.find_by_id(contract_id)

    assert response.id == contract_id


async def test_should_raise_when_contract_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ContractService(repo)
    with pytest.raises(ContractNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_contracts_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = ContractService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_update_contract_when_it_exists() -> None:
    contract_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=contract_id)
    repo.save.side_effect = lambda entity: entity

    service = ContractService(repo)
    new_end = date(2027, 6, 30)
    response = await service.update(
        contract_id, _request(end_date=new_end, status=ContractStatus.ACTIVE)
    )

    assert response.status == ContractStatus.ACTIVE
    assert response.end_date == new_end
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_contract() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ContractService(repo)
    with pytest.raises(ContractNotFoundException):
        await service.update(uuid4(), _request())


async def test_should_delete_contract_when_it_exists() -> None:
    contract_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = ContractService(repo)
    await service.delete(contract_id)

    repo.delete_by_id.assert_awaited_once_with(contract_id)


async def test_should_raise_when_deleting_missing_contract() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = ContractService(repo)
    with pytest.raises(ContractNotFoundException):
        await service.delete(uuid4())
