"""Testes unitários de `NegotiationService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.negotiations.application.dto.negotiation_request_dto import NegotiationRequestDTO
from energyhub.negotiations.application.service.negotiation_service import NegotiationService
from energyhub.negotiations.domain.entity.negotiation import Negotiation
from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.negotiations.domain.exception.negotiation_not_found_exception import (
    NegotiationNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> NegotiationRequestDTO:
    data: dict[str, object] = {"contract_id": uuid4(), "status": NegotiationStatus.DRAFT}
    data.update(overrides)
    return NegotiationRequestDTO(**data)


async def test_should_create_negotiation() -> None:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = NegotiationService(repo)
    response = await service.create(_request())

    assert response.status == NegotiationStatus.DRAFT
    repo.save.assert_awaited_once()


async def test_should_find_negotiation_by_id() -> None:
    negotiation_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Negotiation(id=negotiation_id, contract_id=uuid4())

    service = NegotiationService(repo)
    response = await service.find_by_id(negotiation_id)

    assert response.id == negotiation_id


async def test_should_raise_when_negotiation_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = NegotiationService(repo)
    with pytest.raises(NegotiationNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_negotiations_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([Negotiation(contract_id=uuid4())], 1)

    service = NegotiationService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_update_negotiation_status() -> None:
    negotiation_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Negotiation(id=negotiation_id, contract_id=uuid4())
    repo.save.side_effect = lambda entity: entity

    service = NegotiationService(repo)
    response = await service.update(negotiation_id, _request(status=NegotiationStatus.IN_PROGRESS))

    assert response.status == NegotiationStatus.IN_PROGRESS
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_negotiation() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = NegotiationService(repo)
    with pytest.raises(NegotiationNotFoundException):
        await service.update(uuid4(), _request())


async def test_should_delete_negotiation_when_it_exists() -> None:
    negotiation_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = NegotiationService(repo)
    await service.delete(negotiation_id)

    repo.delete_by_id.assert_awaited_once_with(negotiation_id)


async def test_should_raise_when_deleting_missing_negotiation() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = NegotiationService(repo)
    with pytest.raises(NegotiationNotFoundException):
        await service.delete(uuid4())
