"""Testes de componente do `ClientSearchRouter` (serviço de busca síncrono mockado)."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock
from uuid import uuid4

from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.presentation.router.client_search_router import (
    ClientSearchRouter,
    get_client_search_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _page() -> PageResponse[ClientResponseDTO]:
    dto = ClientResponseDTO(id=uuid4(), cnpj="11222333000181", corporate_name="Usina Alpha")
    return PageResponse.create([dto], 0, 20, 1)


def test_full_text_search_returns_200(router_client: Any) -> None:
    service = Mock()  # serviço de busca é síncrono
    service.search.return_value = _page()
    api = router_client(
        ClientSearchRouter().get_router(), {get_client_search_service: lambda: service}
    )

    response = api.get("/api/v1/search/clients", params={"q": "usina"})

    assert response.status_code == 200
    assert response.json()["total_elements"] == 1


def test_location_filter_returns_200(router_client: Any) -> None:
    service = Mock()
    service.filter_by_location.return_value = _page()
    api = router_client(
        ClientSearchRouter().get_router(), {get_client_search_service: lambda: service}
    )

    response = api.get(
        "/api/v1/search/clients/location", params={"city": "Campinas", "state": "SP"}
    )

    assert response.status_code == 200


def test_advanced_search_returns_200(router_client: Any) -> None:
    service = Mock()
    service.advanced_search.return_value = _page()
    api = router_client(
        ClientSearchRouter().get_router(), {get_client_search_service: lambda: service}
    )

    response = api.post("/api/v1/search/clients/advanced", json={"query": "usina"})

    assert response.status_code == 200
