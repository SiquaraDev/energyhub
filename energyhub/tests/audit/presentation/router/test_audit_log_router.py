"""Testes de componente do `AuditLogRouter` (append-only; serviços mockados)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.audit.application.dto.audit_log_response_dto import AuditLogResponseDTO
from energyhub.audit.domain.entity.audit_action import AuditAction
from energyhub.audit.presentation.router.audit_log_router import (
    AuditLogRouter,
    get_audit_log_service,
    get_create_audit_log_use_case,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _audit_dto() -> AuditLogResponseDTO:
    return AuditLogResponseDTO(
        id=uuid4(),
        user_id=uuid4(),
        action=AuditAction.CREATE,
        entity_type="Client",
        entity_id=uuid4(),
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def _payload() -> dict[str, Any]:
    return {
        "user_id": str(uuid4()),
        "action": "CREATE",
        "entity_type": "Client",
        "entity_id": str(uuid4()),
    }


def test_create_audit_log_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _audit_dto()
    api = router_client(
        AuditLogRouter().get_router(), {get_create_audit_log_use_case: lambda: use_case}
    )

    response = api.post("/api/v1/audit-logs", json=_payload())

    assert response.status_code == 201
    assert response.json()["action"] == "CREATE"


def test_get_audit_log_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _audit_dto()
    api = router_client(AuditLogRouter().get_router(), {get_audit_log_service: lambda: service})

    response = api.get(f"/api/v1/audit-logs/{uuid4()}")

    assert response.status_code == 200


def test_list_audit_logs_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_audit_dto()], 0, 20, 1)
    api = router_client(AuditLogRouter().get_router(), {get_audit_log_service: lambda: service})

    response = api.get("/api/v1/audit-logs")

    assert response.status_code == 200
    assert response.json()["total_elements"] == 1
