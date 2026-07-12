"""Testes unitários de `RoleService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.auth.application.dto.role_request_dto import RoleRequestDTO
from energyhub.auth.application.service.role_service import RoleService
from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.exception.permission_not_found_exception import (
    PermissionNotFoundException,
)
from energyhub.auth.domain.exception.role_already_exists_exception import (
    RoleAlreadyExistsException,
)
from energyhub.auth.domain.exception.role_not_found_exception import RoleNotFoundException
from energyhub.shared.application.dto.page_request import PageRequest


def _service(roles: AsyncMock, permissions: AsyncMock | None = None) -> RoleService:
    return RoleService(roles, permissions or AsyncMock())


async def test_should_create_role_when_name_is_unique() -> None:
    roles = AsyncMock()
    roles.exists_by_name.return_value = False
    roles.save.side_effect = lambda entity: entity

    service = _service(roles)
    response = await service.create(RoleRequestDTO(name="ADMIN", description="Administrador"))

    assert response.name == "ADMIN"
    roles.save.assert_awaited_once()


async def test_should_attach_resolved_permissions_when_creating_role() -> None:
    permission_id = uuid4()
    roles = AsyncMock()
    roles.exists_by_name.return_value = False
    roles.save.side_effect = lambda entity: entity
    permissions = AsyncMock()
    permissions.find_by_id.return_value = Permission(name="CLIENT_READ")

    service = _service(roles, permissions)
    await service.create(RoleRequestDTO(name="OPERATOR", permission_ids=[permission_id]))

    permissions.find_by_id.assert_awaited_once_with(permission_id)
    saved = roles.save.await_args.args[0]
    assert [perm.name for perm in saved.permissions] == ["CLIENT_READ"]


async def test_should_raise_when_role_name_already_exists() -> None:
    roles = AsyncMock()
    roles.exists_by_name.return_value = True

    service = _service(roles)
    with pytest.raises(RoleAlreadyExistsException):
        await service.create(RoleRequestDTO(name="ADMIN"))

    roles.save.assert_not_awaited()


async def test_should_raise_when_permission_id_is_missing() -> None:
    roles = AsyncMock()
    roles.exists_by_name.return_value = False
    permissions = AsyncMock()
    permissions.find_by_id.return_value = None

    service = _service(roles, permissions)
    with pytest.raises(PermissionNotFoundException):
        await service.create(RoleRequestDTO(name="OPERATOR", permission_ids=[uuid4()]))

    roles.save.assert_not_awaited()


async def test_should_find_role_by_id() -> None:
    role_id = uuid4()
    roles = AsyncMock()
    roles.find_by_id.return_value = Role(id=role_id, name="ADMIN")

    service = _service(roles)
    response = await service.find_by_id(role_id)

    assert response.id == role_id


async def test_should_raise_when_role_not_found_by_id() -> None:
    roles = AsyncMock()
    roles.find_by_id.return_value = None

    service = _service(roles)
    with pytest.raises(RoleNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_find_role_by_name() -> None:
    roles = AsyncMock()
    roles.find_by_name.return_value = Role(name="ADMIN")

    service = _service(roles)
    response = await service.find_by_name("ADMIN")

    assert response.name == "ADMIN"


async def test_should_raise_when_role_not_found_by_name() -> None:
    roles = AsyncMock()
    roles.find_by_name.return_value = None

    service = _service(roles)
    with pytest.raises(RoleNotFoundException):
        await service.find_by_name("GHOST")


async def test_should_page_roles_when_find_all() -> None:
    roles = AsyncMock()
    roles.find_page.return_value = ([Role(name="ADMIN")], 1)

    service = _service(roles)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_update_role_when_it_exists() -> None:
    role_id = uuid4()
    roles = AsyncMock()
    roles.find_by_id.return_value = Role(id=role_id, name="ADMIN")
    roles.save.side_effect = lambda entity: entity

    service = _service(roles)
    response = await service.update(role_id, RoleRequestDTO(name="ADMIN", description="Nova"))

    assert response.description == "Nova"
    roles.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_role() -> None:
    roles = AsyncMock()
    roles.find_by_id.return_value = None

    service = _service(roles)
    with pytest.raises(RoleNotFoundException):
        await service.update(uuid4(), RoleRequestDTO(name="ADMIN"))


async def test_should_delete_role_when_it_exists() -> None:
    role_id = uuid4()
    roles = AsyncMock()
    roles.exists_by_id.return_value = True

    service = _service(roles)
    await service.delete(role_id)

    roles.delete_by_id.assert_awaited_once_with(role_id)


async def test_should_raise_when_deleting_missing_role() -> None:
    roles = AsyncMock()
    roles.exists_by_id.return_value = False

    service = _service(roles)
    with pytest.raises(RoleNotFoundException):
        await service.delete(uuid4())
