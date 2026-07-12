"""Testes unitários de `NotificationService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.notifications.application.dto.notification_request_dto import (
    NotificationRequestDTO,
)
from energyhub.notifications.application.service.notification_service import NotificationService
from energyhub.notifications.domain.entity.notification import Notification
from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.notifications.domain.exception.notification_not_found_exception import (
    NotificationNotFoundException,
)
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> NotificationRequestDTO:
    data: dict[str, object] = {
        "user_id": uuid4(),
        "title": "Bem-vindo",
        "message": "Sua conta foi criada",
        "status": NotificationStatus.PENDING,
    }
    data.update(overrides)
    return NotificationRequestDTO(**data)


def _entity(**overrides: object) -> Notification:
    data: dict[str, object] = {
        "user_id": uuid4(),
        "title": "Bem-vindo",
        "message": "Sua conta foi criada",
        "status": NotificationStatus.PENDING,
    }
    data.update(overrides)
    return Notification(**data)


async def test_should_create_notification() -> None:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = NotificationService(repo)
    response = await service.create(_request())

    assert response.title == "Bem-vindo"
    repo.save.assert_awaited_once()


async def test_should_find_notification_by_id() -> None:
    notification_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=notification_id)

    service = NotificationService(repo)
    response = await service.find_by_id(notification_id)

    assert response.id == notification_id


async def test_should_raise_when_notification_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = NotificationService(repo)
    with pytest.raises(NotificationNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_notifications_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = NotificationService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_update_notification_when_it_exists() -> None:
    notification_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=notification_id)
    repo.save.side_effect = lambda entity: entity

    service = NotificationService(repo)
    response = await service.update(
        notification_id,
        _request(title="Atualizado", message="Novo texto", status=NotificationStatus.SENT),
    )

    assert response.title == "Atualizado"
    assert response.status == NotificationStatus.SENT
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_notification() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = NotificationService(repo)
    with pytest.raises(NotificationNotFoundException):
        await service.update(uuid4(), _request())


async def test_should_delete_notification_when_it_exists() -> None:
    notification_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = NotificationService(repo)
    await service.delete(notification_id)

    repo.delete_by_id.assert_awaited_once_with(notification_id)


async def test_should_raise_when_deleting_missing_notification() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = NotificationService(repo)
    with pytest.raises(NotificationNotFoundException):
        await service.delete(uuid4())
