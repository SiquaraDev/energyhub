"""Testes unitários de `UserService` (colaboradores mockados; sem banco/broker/rede)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.auth.application.dto.user_request_dto import UserRequestDTO
from energyhub.auth.application.service.user_service import UserService
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.auth.domain.exception.user_already_exists_exception import (
    UserAlreadyExistsException,
)
from energyhub.auth.domain.exception.user_not_found_exception import UserNotFoundException
from energyhub.shared.application.dto.page_request import PageRequest


def _valid_request(**overrides: object) -> UserRequestDTO:
    data: dict[str, object] = {
        "username": "jsilva",
        "password": "segredo123",
        "email": "jsilva@energyhub.local",
        "full_name": "João Silva",
        "active": True,
        "role_ids": [],
    }
    data.update(overrides)
    return UserRequestDTO(**data)


def _service(
    users: AsyncMock, roles: AsyncMock | None = None, producer: AsyncMock | None = None
) -> UserService:
    return UserService(users, roles or AsyncMock(), event_producer=producer)


async def test_should_create_user_and_save_once_when_data_is_valid() -> None:
    users = AsyncMock()
    users.exists_by_username.return_value = False
    users.exists_by_email.return_value = False
    users.save.side_effect = lambda entity: entity

    service = _service(users)
    response = await service.create(_valid_request())

    assert response.username == "jsilva"
    assert response.email == "jsilva@energyhub.local"
    users.save.assert_awaited_once()
    # A senha é hasheada antes de persistir (nunca em texto puro).
    saved_user = users.save.await_args.args[0]
    assert isinstance(saved_user, User)
    assert saved_user.password != "segredo123"


async def test_should_publish_created_event_when_producer_is_present() -> None:
    users = AsyncMock()
    users.exists_by_username.return_value = False
    users.exists_by_email.return_value = False
    users.save.side_effect = lambda entity: entity
    producer = AsyncMock()

    service = _service(users, producer=producer)
    await service.create(_valid_request())

    producer.publish_user_created.assert_awaited_once()


async def test_should_resolve_roles_when_role_ids_are_provided() -> None:
    role_id = uuid4()
    users = AsyncMock()
    users.exists_by_username.return_value = False
    users.exists_by_email.return_value = False
    users.save.side_effect = lambda entity: entity
    roles = AsyncMock()
    roles.find_by_id.return_value = Role(name="ADMIN")

    service = _service(users, roles)
    await service.create(_valid_request(role_ids=[role_id]))

    roles.find_by_id.assert_awaited_once_with(role_id)
    saved_user = users.save.await_args.args[0]
    assert [role.name for role in saved_user.roles] == ["ADMIN"]


async def test_should_raise_when_username_already_exists() -> None:
    users = AsyncMock()
    users.exists_by_username.return_value = True

    service = _service(users)
    with pytest.raises(UserAlreadyExistsException):
        await service.create(_valid_request())

    users.save.assert_not_awaited()


async def test_should_raise_when_email_already_exists() -> None:
    users = AsyncMock()
    users.exists_by_username.return_value = False
    users.exists_by_email.return_value = True

    service = _service(users)
    with pytest.raises(UserAlreadyExistsException):
        await service.create(_valid_request())

    users.save.assert_not_awaited()


async def test_should_raise_when_role_id_does_not_exist() -> None:
    users = AsyncMock()
    users.exists_by_username.return_value = False
    users.exists_by_email.return_value = False
    roles = AsyncMock()
    roles.find_by_id.return_value = None

    service = _service(users, roles)
    with pytest.raises(RoleNotFoundException):
        await service.create(_valid_request(role_ids=[uuid4()]))

    users.save.assert_not_awaited()


async def test_should_return_user_when_found_by_id() -> None:
    user_id = uuid4()
    users = AsyncMock()
    users.find_by_id.return_value = User(
        id=user_id, username="jsilva", password="hash", email="jsilva@energyhub.local"
    )

    service = _service(users)
    response = await service.find_by_id(user_id)

    assert response.id == user_id
    assert response.username == "jsilva"


async def test_should_raise_when_user_not_found_by_id() -> None:
    users = AsyncMock()
    users.find_by_id.return_value = None

    service = _service(users)
    with pytest.raises(UserNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_users_when_find_all() -> None:
    users = AsyncMock()
    users.find_page.return_value = (
        [User(username="a", password="h", email="a@x.io")],
        1,
    )

    service = _service(users)
    page = await service.find_all(PageRequest(page=0, size=10))

    assert page.total_elements == 1
    assert len(page.content) == 1
    assert page.content[0].username == "a"


async def test_should_update_user_when_it_exists() -> None:
    user_id = uuid4()
    users = AsyncMock()
    users.find_by_id.return_value = User(
        id=user_id, username="jsilva", password="old", email="jsilva@energyhub.local"
    )
    users.save.side_effect = lambda entity: entity

    service = _service(users)
    response = await service.update(user_id, _valid_request(full_name="Novo Nome"))

    assert response.full_name == "Novo Nome"
    users.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_user() -> None:
    users = AsyncMock()
    users.find_by_id.return_value = None

    service = _service(users)
    with pytest.raises(UserNotFoundException):
        await service.update(uuid4(), _valid_request())

    users.save.assert_not_awaited()


async def test_should_delete_user_when_it_exists() -> None:
    user_id = uuid4()
    users = AsyncMock()
    users.exists_by_id.return_value = True

    service = _service(users)
    await service.delete(user_id)

    users.delete_by_id.assert_awaited_once_with(user_id)


async def test_should_raise_when_deleting_missing_user() -> None:
    users = AsyncMock()
    users.exists_by_id.return_value = False

    service = _service(users)
    with pytest.raises(UserNotFoundException):
        await service.delete(uuid4())

    users.delete_by_id.assert_not_awaited()
