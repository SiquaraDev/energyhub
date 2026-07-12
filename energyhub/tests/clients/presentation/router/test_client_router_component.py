"""Testes de componente do `ClientRouter` (TestClient + serviços mockados; sem banco).

Exercitam roteamento, status HTTP, serialização e os guards de autorização (via override de
`get_current_user`) sem infraestrutura. As regras de negócio ficam nos testes unitários do serviço.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.clients.domain.entity.contact_type import ContactType
from energyhub.clients.presentation.router.client_router import (
    ClientRouter,
    get_client_service,
    get_contact_service,
    get_create_client_use_case,
)
from energyhub.shared.application.dto.page_response import PageResponse

VALID_CNPJ = "11222333000181"


def _client_dto() -> ClientResponseDTO:
    return ClientResponseDTO(id=uuid4(), cnpj=VALID_CNPJ, corporate_name="Usina Alpha")


def _contact_dto(client_id: Any) -> ContactResponseDTO:
    return ContactResponseDTO(
        id=uuid4(), client_id=client_id, name="Maria", type=ContactType.PRIMARY
    )


def _payload() -> dict[str, Any]:
    return {"cnpj": VALID_CNPJ, "corporate_name": "Usina Alpha"}


@pytest.fixture
def service() -> AsyncMock:
    return AsyncMock()


def test_create_client_returns_201(router_client: Any, service: AsyncMock) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _client_dto()
    api = router_client(ClientRouter().get_router(), {get_create_client_use_case: lambda: use_case})

    response = api.post("/api/v1/clients", json=_payload())

    assert response.status_code == 201
    assert response.json()["cnpj"] == VALID_CNPJ


def test_get_client_returns_200(router_client: Any, service: AsyncMock) -> None:
    service.find_by_id.return_value = _client_dto()
    api = router_client(ClientRouter().get_router(), {get_client_service: lambda: service})

    response = api.get(f"/api/v1/clients/{uuid4()}")

    assert response.status_code == 200
    assert response.json()["corporate_name"] == "Usina Alpha"


def test_list_clients_returns_200(router_client: Any, service: AsyncMock) -> None:
    service.find_all.return_value = PageResponse.create([_client_dto()], 0, 20, 1)
    api = router_client(ClientRouter().get_router(), {get_client_service: lambda: service})

    response = api.get("/api/v1/clients")

    assert response.status_code == 200
    assert response.json()["total_elements"] == 1


def test_update_client_returns_200(router_client: Any, service: AsyncMock) -> None:
    service.update.return_value = _client_dto()
    api = router_client(ClientRouter().get_router(), {get_client_service: lambda: service})

    response = api.put(f"/api/v1/clients/{uuid4()}", json=_payload())

    assert response.status_code == 200


def test_delete_client_returns_204(router_client: Any, service: AsyncMock) -> None:
    service.delete.return_value = None
    api = router_client(ClientRouter().get_router(), {get_client_service: lambda: service})

    response = api.delete(f"/api/v1/clients/{uuid4()}")

    assert response.status_code == 204


def test_add_contact_returns_201(router_client: Any) -> None:
    client_id = uuid4()
    contacts = AsyncMock()
    contacts.create.return_value = _contact_dto(client_id)
    api = router_client(ClientRouter().get_router(), {get_contact_service: lambda: contacts})

    response = api.post(
        f"/api/v1/clients/{client_id}/contacts",
        json={"name": "Maria", "type": "PRIMARY"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Maria"


def test_list_contacts_returns_200(router_client: Any) -> None:
    client_id = uuid4()
    contacts = AsyncMock()
    contacts.find_by_client_id.return_value = [_contact_dto(client_id)]
    api = router_client(ClientRouter().get_router(), {get_contact_service: lambda: contacts})

    response = api.get(f"/api/v1/clients/{client_id}/contacts")

    assert response.status_code == 200
    assert len(response.json()) == 1
