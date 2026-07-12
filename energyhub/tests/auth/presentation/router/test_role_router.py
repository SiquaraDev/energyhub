"""Testes de componente do `RoleRouter` (serviço mockado; sem banco)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.auth.application.dto.role_response_dto import RoleResponseDTO
from energyhub.auth.presentation.router.role_router import RoleRouter, get_role_service
from energyhub.shared.application.dto.page_response import PageResponse


def _role_dto() -> RoleResponseDTO:
    return RoleResponseDTO(id=uuid4(), name="ADMIN")


def test_create_role_returns_201(router_client: Any) -> None:
    service = AsyncMock()
    service.create.return_value = _role_dto()
    api = router_client(RoleRouter().get_router(), {get_role_service: lambda: service})

    response = api.post("/api/v1/roles", json={"name": "ADMIN"})

    assert response.status_code == 201
    assert response.json()["name"] == "ADMIN"


def test_get_role_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _role_dto()
    api = router_client(RoleRouter().get_router(), {get_role_service: lambda: service})

    response = api.get(f"/api/v1/roles/{uuid4()}")

    assert response.status_code == 200


def test_list_roles_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_role_dto()], 0, 20, 1)
    api = router_client(RoleRouter().get_router(), {get_role_service: lambda: service})

    response = api.get("/api/v1/roles")

    assert response.status_code == 200


def test_update_role_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _role_dto()
    api = router_client(RoleRouter().get_router(), {get_role_service: lambda: service})

    response = api.put(f"/api/v1/roles/{uuid4()}", json={"name": "ADMIN"})

    assert response.status_code == 200


def test_delete_role_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(RoleRouter().get_router(), {get_role_service: lambda: service})

    response = api.delete(f"/api/v1/roles/{uuid4()}")

    assert response.status_code == 204
