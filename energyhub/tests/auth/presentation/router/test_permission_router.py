"""Testes de componente do `PermissionRouter` (serviço mockado; sem banco)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.auth.application.dto.permission_response_dto import PermissionResponseDTO
from energyhub.auth.presentation.router.permission_router import (
    PermissionRouter,
    get_permission_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _permission_dto() -> PermissionResponseDTO:
    return PermissionResponseDTO(id=uuid4(), name="CLIENT_CREATE")


def test_create_permission_returns_201(router_client: Any) -> None:
    service = AsyncMock()
    service.create.return_value = _permission_dto()
    api = router_client(PermissionRouter().get_router(), {get_permission_service: lambda: service})

    response = api.post("/api/v1/permissions", json={"name": "CLIENT_CREATE"})

    assert response.status_code == 201
    assert response.json()["name"] == "CLIENT_CREATE"


def test_get_permission_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _permission_dto()
    api = router_client(PermissionRouter().get_router(), {get_permission_service: lambda: service})

    response = api.get(f"/api/v1/permissions/{uuid4()}")

    assert response.status_code == 200


def test_list_permissions_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_permission_dto()], 0, 20, 1)
    api = router_client(PermissionRouter().get_router(), {get_permission_service: lambda: service})

    response = api.get("/api/v1/permissions")

    assert response.status_code == 200


def test_update_permission_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _permission_dto()
    api = router_client(PermissionRouter().get_router(), {get_permission_service: lambda: service})

    response = api.put(f"/api/v1/permissions/{uuid4()}", json={"name": "CLIENT_CREATE"})

    assert response.status_code == 200


def test_delete_permission_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(PermissionRouter().get_router(), {get_permission_service: lambda: service})

    response = api.delete(f"/api/v1/permissions/{uuid4()}")

    assert response.status_code == 204
