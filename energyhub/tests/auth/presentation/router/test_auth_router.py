"""Testes de componente do `AuthRouter` (login público; serviço mockado)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.auth.application.dto.login_response_dto import LoginResponseDTO
from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.presentation.router.auth_router import AuthRouter, get_authentication_service


def test_login_returns_token(router_client: Any) -> None:
    auth = AsyncMock()
    auth.login.return_value = LoginResponseDTO(
        access_token="jwt-token",
        user=UserResponseDTO(id=uuid4(), username="admin", email="admin@energyhub.local"),
    )
    api = router_client(AuthRouter().get_router(), {get_authentication_service: lambda: auth})

    response = api.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "ChangeMe123!"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "jwt-token"
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "admin"
