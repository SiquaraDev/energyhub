"""Testes unitários de `AuthenticationService` (login com senha hasheada real)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from energyhub.auth.application.dto.login_request_dto import LoginRequestDTO
from energyhub.auth.application.service.authentication_service import AuthenticationService
from energyhub.auth.domain.entity.user import User
from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.shared.infrastructure.security.password_hasher import get_password_hash

PLAIN_PASSWORD = "ChangeMe123!"


def _user(active: bool = True) -> User:
    return User(
        username="admin",
        password=get_password_hash(PLAIN_PASSWORD),
        email="admin@energyhub.local",
        active=active,
    )


async def test_should_return_token_when_credentials_are_valid() -> None:
    users = AsyncMock()
    users.find_by_username.return_value = _user()

    service = AuthenticationService(users)
    response = await service.login(LoginRequestDTO(username="admin", password=PLAIN_PASSWORD))

    assert response.access_token
    assert response.token_type == "bearer"
    assert response.user.username == "admin"


async def test_should_raise_when_user_does_not_exist() -> None:
    users = AsyncMock()
    users.find_by_username.return_value = None

    service = AuthenticationService(users)
    with pytest.raises(InvalidCredentialsException):
        await service.login(LoginRequestDTO(username="ghost", password=PLAIN_PASSWORD))


async def test_should_raise_when_password_is_wrong() -> None:
    users = AsyncMock()
    users.find_by_username.return_value = _user()

    service = AuthenticationService(users)
    with pytest.raises(InvalidCredentialsException):
        await service.login(LoginRequestDTO(username="admin", password="senhaErrada"))


async def test_should_raise_when_user_is_inactive() -> None:
    users = AsyncMock()
    users.find_by_username.return_value = _user(active=False)

    service = AuthenticationService(users)
    with pytest.raises(InvalidCredentialsException):
        await service.login(LoginRequestDTO(username="admin", password=PLAIN_PASSWORD))
