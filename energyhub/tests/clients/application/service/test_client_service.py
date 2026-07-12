"""Testes unitários de `ClientService` (colaboradores mockados; sem banco/broker/rede)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.service.client_service import ClientService
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.domain.exception.client_already_exists_exception import (
    ClientAlreadyExistsException,
)
from energyhub.clients.domain.exception.client_not_found_exception import ClientNotFoundException
from energyhub.shared.application.dto.page_request import PageRequest

VALID_CNPJ = "11222333000181"


def _valid_request(**overrides: object) -> ClientRequestDTO:
    data: dict[str, object] = {
        "cnpj": VALID_CNPJ,
        "corporate_name": "Usina Alpha",
        "city": "São Paulo",
        "state": "SP",
        "active": True,
    }
    data.update(overrides)
    return ClientRequestDTO(**data)


async def test_should_create_client_and_save_once_when_data_is_valid() -> None:
    repo = AsyncMock()
    repo.exists_by_cnpj.return_value = False
    repo.save.side_effect = lambda entity: entity

    service = ClientService(repo)
    response = await service.create(_valid_request())

    assert response.cnpj == VALID_CNPJ
    assert response.corporate_name == "Usina Alpha"
    repo.save.assert_awaited_once()
    saved = repo.save.await_args.args[0]
    assert isinstance(saved, Client)


async def test_should_publish_created_event_when_producer_is_present() -> None:
    repo = AsyncMock()
    repo.exists_by_cnpj.return_value = False
    repo.save.side_effect = lambda entity: entity
    producer = AsyncMock()

    service = ClientService(repo, event_producer=producer)
    await service.create(_valid_request())

    producer.publish_client_created.assert_awaited_once()


async def test_should_raise_when_cnpj_already_exists() -> None:
    repo = AsyncMock()
    repo.exists_by_cnpj.return_value = True
    producer = AsyncMock()

    service = ClientService(repo, event_producer=producer)
    with pytest.raises(ClientAlreadyExistsException):
        await service.create(_valid_request())

    repo.save.assert_not_awaited()
    producer.publish_client_created.assert_not_awaited()


async def test_should_return_client_when_found_by_id() -> None:
    client_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Client(
        id=client_id, cnpj=VALID_CNPJ, corporate_name="Usina Alpha"
    )

    service = ClientService(repo)
    response = await service.find_by_id(client_id)

    assert response.id == client_id
    assert response.cnpj == VALID_CNPJ


async def test_should_raise_when_client_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ClientService(repo)
    with pytest.raises(ClientNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_clients_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([Client(cnpj=VALID_CNPJ, corporate_name="Alpha")], 1)

    service = ClientService(repo)
    page = await service.find_all(PageRequest(page=0, size=10))

    assert page.total_elements == 1
    assert page.content[0].corporate_name == "Alpha"


async def test_should_update_client_when_it_exists() -> None:
    client_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Client(id=client_id, cnpj=VALID_CNPJ, corporate_name="Antigo")
    repo.save.side_effect = lambda entity: entity

    service = ClientService(repo)
    response = await service.update(client_id, _valid_request(corporate_name="Novo Nome"))

    assert response.corporate_name == "Novo Nome"
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_client() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ClientService(repo)
    with pytest.raises(ClientNotFoundException):
        await service.update(uuid4(), _valid_request())

    repo.save.assert_not_awaited()


async def test_should_delete_client_when_it_exists() -> None:
    client_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = ClientService(repo)
    await service.delete(client_id)

    repo.delete_by_id.assert_awaited_once_with(client_id)


async def test_should_raise_when_deleting_missing_client() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = ClientService(repo)
    with pytest.raises(ClientNotFoundException):
        await service.delete(uuid4())

    repo.delete_by_id.assert_not_awaited()
