"""Testes unitários de `AuditLogService` (append-only: create + finders)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.audit.application.dto.audit_log_request_dto import AuditLogRequestDTO
from energyhub.audit.application.service.audit_log_service import AuditLogService
from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.domain.entity.audit_log import AuditLog
from energyhub.audit.domain.exception.audit_log_not_found_exception import (
    AuditLogNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> AuditLogRequestDTO:
    data: dict[str, object] = {
        "user_id": uuid4(),
        "action": AuditAction.CREATE,
        "entity_type": "Client",
        "entity_id": uuid4(),
        "details": {"cnpj": "11222333000181"},
    }
    data.update(overrides)
    return AuditLogRequestDTO(**data)


def _entity(**overrides: object) -> AuditLog:
    data: dict[str, object] = {
        "user_id": uuid4(),
        "action": AuditAction.CREATE,
        "entity_type": "Client",
        "entity_id": uuid4(),
        "details": {},
    }
    data.update(overrides)
    return AuditLog(**data)


async def test_should_create_audit_log() -> None:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = AuditLogService(repo)
    response = await service.create(_request())

    assert response.action == AuditAction.CREATE
    assert response.entity_type == "Client"
    repo.save.assert_awaited_once()


async def test_should_find_audit_log_by_id() -> None:
    audit_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=audit_id)

    service = AuditLogService(repo)
    response = await service.find_by_id(audit_id)

    assert response.id == audit_id


async def test_should_raise_when_audit_log_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = AuditLogService(repo)
    with pytest.raises(AuditLogNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_audit_logs_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = AuditLogService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1
