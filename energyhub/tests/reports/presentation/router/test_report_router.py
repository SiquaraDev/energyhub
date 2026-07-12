"""Testes de componente do `ReportRouter` (serviços mockados; sem banco)."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.reports.application.dto.report_response_dto import ReportResponseDTO
from energyhub.reports.presentation.router.report_router import (
    ReportRouter,
    get_create_report_use_case,
    get_report_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _report_dto() -> ReportResponseDTO:
    return ReportResponseDTO(id=uuid4(), report_type="MONTHLY_CONSUMPTION", generated_by=uuid4())


def _payload() -> dict[str, Any]:
    return {"report_type": "MONTHLY_CONSUMPTION", "generated_by": str(uuid4())}


def test_create_report_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _report_dto()
    api = router_client(ReportRouter().get_router(), {get_create_report_use_case: lambda: use_case})

    response = api.post("/api/v1/reports", json=_payload())

    assert response.status_code == 201


def test_get_report_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _report_dto()
    api = router_client(ReportRouter().get_router(), {get_report_service: lambda: service})

    response = api.get(f"/api/v1/reports/{uuid4()}")

    assert response.status_code == 200


def test_list_reports_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_report_dto()], 0, 20, 1)
    api = router_client(ReportRouter().get_router(), {get_report_service: lambda: service})

    response = api.get("/api/v1/reports")

    assert response.status_code == 200


def test_update_report_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _report_dto()
    api = router_client(ReportRouter().get_router(), {get_report_service: lambda: service})

    response = api.put(f"/api/v1/reports/{uuid4()}", json=_payload())

    assert response.status_code == 200


def test_delete_report_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(ReportRouter().get_router(), {get_report_service: lambda: service})

    response = api.delete(f"/api/v1/reports/{uuid4()}")

    assert response.status_code == 204
