"""Testes unitários de `PermissionService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.auth.application.dto.permission_request_dto import PermissionRequestDTO
from energyhub.auth.application.service.permission_service import PermissionService
from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.exception.permission_already_exists_exception import (
    PermissionAlreadyExistsException,
)
from energyhub.auth.domain.exception.permission_not_found_exception import (
    PermissionNotFoundException,
)
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.shared.application.dto.page_request import PageRequest


async def test_should_create_permission_when_name_is_unique() -> None:
    repo = AsyncMock()
    repo.exists_by_name.return_value = False
    repo.save.side_effect = lambda entity: entity

    service = PermissionService(repo)
    response = await service.create(PermissionRequestDTO(name="CLIENT_CREATE"))

    assert response.name == "CLIENT_CREATE"
    repo.save.assert_awaited_once()


async def test_should_raise_when_permission_name_already_exists() -> None:
    repo = AsyncMock()
    repo.exists_by_name.return_value = True

    service = PermissionService(repo)
    with pytest.raises(PermissionAlreadyExistsException):
        await service.create(PermissionRequestDTO(name="CLIENT_CREATE"))

    repo.save.assert_not_awaited()


async def test_should_find_permission_by_id() -> None:
    permission_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Permission(id=permission_id, name="CLIENT_READ")

    service = PermissionService(repo)
    response = await service.find_by_id(permission_id)

    assert response.id == permission_id


async def test_should_raise_when_permission_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = PermissionService(repo)
    with pytest.raises(PermissionNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_permissions_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([Permission(name="CLIENT_READ")], 1)

    service = PermissionService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_list_permissions_of_a_role_by_name() -> None:
    repo = AsyncMock()
    roles = AsyncMock()
    roles.find_by_name.return_value = Role(
        name="ADMIN", permissions=[Permission(name="CLIENT_READ")]
    )

    service = PermissionService(repo, role_repository=roles)
    result = await service.find_by_role_name("ADMIN")

    assert [dto.name for dto in result] == ["CLIENT_READ"]


async def test_should_raise_runtime_error_when_role_repository_is_absent() -> None:
    repo = AsyncMock()

    service = PermissionService(repo)
    with pytest.raises(RuntimeError):
        await service.find_by_role_name("ADMIN")


async def test_should_raise_when_role_not_found_by_name() -> None:
    repo = AsyncMock()
    roles = AsyncMock()
    roles.find_by_name.return_value = None

    service = PermissionService(repo, role_repository=roles)
    with pytest.raises(RoleNotFoundException):
        await service.find_by_role_name("GHOST")


async def test_should_update_permission_when_it_exists() -> None:
    permission_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = Permission(id=permission_id, name="CLIENT_READ")
    repo.save.side_effect = lambda entity: entity

    service = PermissionService(repo)
    response = await service.update(
        permission_id, PermissionRequestDTO(name="CLIENT_READ", description="Ler clientes")
    )

    assert response.description == "Ler clientes"
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_permission() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = PermissionService(repo)
    with pytest.raises(PermissionNotFoundException):
        await service.update(uuid4(), PermissionRequestDTO(name="CLIENT_READ"))


async def test_should_delete_permission_when_it_exists() -> None:
    permission_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = PermissionService(repo)
    await service.delete(permission_id)

    repo.delete_by_id.assert_awaited_once_with(permission_id)


async def test_should_raise_when_deleting_missing_permission() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = PermissionService(repo)
    with pytest.raises(PermissionNotFoundException):
        await service.delete(uuid4())
