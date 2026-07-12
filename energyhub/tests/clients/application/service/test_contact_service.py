"""Testes unitários de `ContactService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.clients.application.dto.contact_request_dto import ContactRequestDTO
from energyhub.clients.application.service.contact_service import ContactService
from energyhub.clients.domain.entity.contact import Contact
from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.clients.domain.exception.client_not_found_exception import ClientNotFoundException


def _request() -> ContactRequestDTO:
    return ContactRequestDTO(
        name="Maria Souza",
        type=ContactType.PRIMARY,
        email="maria@usina.com",
        phone="11999998888",
        position="Gerente",
    )


async def test_should_create_contact_when_client_exists() -> None:
    client_id = uuid4()
    contacts = AsyncMock()
    contacts.save.side_effect = lambda entity: entity
    clients = AsyncMock()
    clients.exists_by_id.return_value = True

    service = ContactService(contacts, clients)
    response = await service.create(client_id, _request())

    assert response.name == "Maria Souza"
    assert response.client_id == client_id
    contacts.save.assert_awaited_once()
    saved = contacts.save.await_args.args[0]
    assert isinstance(saved, Contact)


async def test_should_raise_when_client_does_not_exist() -> None:
    contacts = AsyncMock()
    clients = AsyncMock()
    clients.exists_by_id.return_value = False

    service = ContactService(contacts, clients)
    with pytest.raises(ClientNotFoundException):
        await service.create(uuid4(), _request())

    contacts.save.assert_not_awaited()


async def test_should_list_contacts_by_client_id() -> None:
    client_id = uuid4()
    contacts = AsyncMock()
    contacts.find_by_client_id.return_value = [
        Contact(client_id=client_id, name="Maria", type=ContactType.PRIMARY),
        Contact(client_id=client_id, name="João", type=ContactType.BILLING),
    ]
    clients = AsyncMock()

    service = ContactService(contacts, clients)
    result = await service.find_by_client_id(client_id)

    assert [dto.name for dto in result] == ["Maria", "João"]
    contacts.find_by_client_id.assert_awaited_once_with(client_id)
