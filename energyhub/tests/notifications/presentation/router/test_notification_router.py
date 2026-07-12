"""Testes de componente do `NotificationRouter` (serviços mockados; sem banco)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.notifications.application.dto.notification_response_dto import (
    NotificationResponseDTO,
)
from energyhub.notifications.domain.entity.notification_status import NotificationStatus
from energyhub.notifications.presentation.router.notification_router import (
    NotificationRouter,
    get_create_notification_use_case,
    get_notification_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _notification_dto() -> NotificationResponseDTO:
    return NotificationResponseDTO(
        id=uuid4(),
        user_id=uuid4(),
        title="Bem-vindo",
        message="Sua conta foi criada",
        status=NotificationStatus.PENDING,
    )


def _payload() -> dict[str, Any]:
    return {"user_id": str(uuid4()), "title": "Bem-vindo", "message": "Sua conta foi criada"}


def test_create_notification_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _notification_dto()
    api = router_client(
        NotificationRouter().get_router(), {get_create_notification_use_case: lambda: use_case}
    )

    response = api.post("/api/v1/notifications", json=_payload())

    assert response.status_code == 201


def test_get_notification_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _notification_dto()
    api = router_client(
        NotificationRouter().get_router(), {get_notification_service: lambda: service}
    )

    response = api.get(f"/api/v1/notifications/{uuid4()}")

    assert response.status_code == 200


def test_list_notifications_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_notification_dto()], 0, 20, 1)
    api = router_client(
        NotificationRouter().get_router(), {get_notification_service: lambda: service}
    )

    response = api.get("/api/v1/notifications")

    assert response.status_code == 200


def test_update_notification_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _notification_dto()
    api = router_client(
        NotificationRouter().get_router(), {get_notification_service: lambda: service}
    )

    response = api.put(f"/api/v1/notifications/{uuid4()}", json=_payload())

    assert response.status_code == 200


def test_delete_notification_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(
        NotificationRouter().get_router(), {get_notification_service: lambda: service}
    )

    response = api.delete(f"/api/v1/notifications/{uuid4()}")

    assert response.status_code == 204
