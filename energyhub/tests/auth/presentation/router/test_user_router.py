"""Testes de componente do `UserRouter` (serviços mockados; sem banco)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.presentation.router.user_router import (
    UserRouter,
    get_create_user_use_case,
    get_user_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _user_dto() -> UserResponseDTO:
    return UserResponseDTO(id=uuid4(), username="jsilva", email="jsilva@energyhub.local")


def _payload() -> dict[str, Any]:
    return {"username": "jsilva", "password": "segredo123", "email": "jsilva@energyhub.local"}


def test_create_user_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _user_dto()
    api = router_client(UserRouter().get_router(), {get_create_user_use_case: lambda: use_case})

    response = api.post("/api/v1/users", json=_payload())

    assert response.status_code == 201
    assert response.json()["username"] == "jsilva"


def test_get_user_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _user_dto()
    api = router_client(UserRouter().get_router(), {get_user_service: lambda: service})

    response = api.get(f"/api/v1/users/{uuid4()}")

    assert response.status_code == 200


def test_list_users_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_user_dto()], 0, 20, 1)
    api = router_client(UserRouter().get_router(), {get_user_service: lambda: service})

    response = api.get("/api/v1/users")

    assert response.status_code == 200
    assert response.json()["total_elements"] == 1


def test_update_user_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _user_dto()
    api = router_client(UserRouter().get_router(), {get_user_service: lambda: service})

    response = api.put(f"/api/v1/users/{uuid4()}", json=_payload())

    assert response.status_code == 200


def test_delete_user_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(UserRouter().get_router(), {get_user_service: lambda: service})

    response = api.delete(f"/api/v1/users/{uuid4()}")

    assert response.status_code == 204
