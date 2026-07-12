"""Testes unitários das entidades de `auth` (validação + associações)."""

from __future__ import annotations

import pytest

from energyhub.auth.domain.entity.permission import Permission
from energyhub.auth.domain.entity.role import Role
from energyhub.auth.domain.entity.user import User
from energyhub.shared.domain.exception.validation_exception import ValidationException


def test_user_requires_username() -> None:
    with pytest.raises(ValidationException):
        User(username="  ", password="x", email="a@b.io")


def test_user_requires_valid_email() -> None:
    with pytest.raises(ValidationException):
        User(username="admin", password="x", email="sem-arroba")


def test_user_add_and_remove_role_is_bidirectional() -> None:
    user = User(username="admin", password="x", email="a@b.io")
    role = Role(name="ADMIN")

    user.add_role(role)
    assert role in user.roles
    assert user in role.users

    user.remove_role(role)
    assert role not in user.roles
    assert user not in role.users


def test_role_requires_name() -> None:
    with pytest.raises(ValidationException):
        Role(name="   ")


def test_role_add_permission_is_idempotent() -> None:
    role = Role(name="ADMIN")
    permission = Permission(name="CLIENT_READ")

    role.add_permission(permission)
    role.add_permission(permission)  # idempotente
    assert role.permissions.count(permission) == 1

    role.remove_permission(permission)
    assert permission not in role.permissions


def test_permission_requires_name() -> None:
    with pytest.raises(ValidationException):
        Permission(name="")
