"""Testes unitários de `ReportService` (colaboradores mockados)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from energyhub.reports.application.dto.report_request_dto import ReportRequestDTO
from energyhub.reports.application.service.report_service import ReportService
from energyhub.reports.domain.entity.report import Report
from energyhub.reports.domain.exception.report_not_found_exception import ReportNotFoundException
from energyhub.shared.application.dto.page_request import PageRequest


def _request(**overrides: object) -> ReportRequestDTO:
    data: dict[str, object] = {
        "report_type": "MONTHLY_CONSUMPTION",
        "generated_by": uuid4(),
        "parameters": {"month": "2026-01"},
        "file_path": None,
    }
    data.update(overrides)
    return ReportRequestDTO(**data)


def _entity(**overrides: object) -> Report:
    data: dict[str, object] = {
        "report_type": "MONTHLY_CONSUMPTION",
        "generated_by": uuid4(),
        "parameters": {"month": "2026-01"},
    }
    data.update(overrides)
    return Report(**data)


async def test_should_create_report() -> None:
    repo = AsyncMock()
    repo.save.side_effect = lambda entity: entity

    service = ReportService(repo)
    response = await service.create(_request())

    assert response.report_type == "MONTHLY_CONSUMPTION"
    repo.save.assert_awaited_once()


async def test_should_find_report_by_id() -> None:
    report_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=report_id)

    service = ReportService(repo)
    response = await service.find_by_id(report_id)

    assert response.id == report_id


async def test_should_raise_when_report_not_found_by_id() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ReportService(repo)
    with pytest.raises(ReportNotFoundException):
        await service.find_by_id(uuid4())


async def test_should_page_reports_when_find_all() -> None:
    repo = AsyncMock()
    repo.find_page.return_value = ([_entity()], 1)

    service = ReportService(repo)
    page = await service.find_all(PageRequest(page=0, size=5))

    assert page.total_elements == 1


async def test_should_update_report_parameters_and_file_path() -> None:
    report_id = uuid4()
    repo = AsyncMock()
    repo.find_by_id.return_value = _entity(id=report_id)
    repo.save.side_effect = lambda entity: entity

    service = ReportService(repo)
    response = await service.update(
        report_id, _request(parameters={"month": "2026-02"}, file_path="/tmp/report.pdf")
    )

    assert response.parameters == {"month": "2026-02"}
    assert response.file_path == "/tmp/report.pdf"
    repo.save.assert_awaited_once()


async def test_should_raise_when_updating_missing_report() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    service = ReportService(repo)
    with pytest.raises(ReportNotFoundException):
        await service.update(uuid4(), _request())


async def test_should_delete_report_when_it_exists() -> None:
    report_id = uuid4()
    repo = AsyncMock()
    repo.exists_by_id.return_value = True

    service = ReportService(repo)
    await service.delete(report_id)

    repo.delete_by_id.assert_awaited_once_with(report_id)


async def test_should_raise_when_deleting_missing_report() -> None:
    repo = AsyncMock()
    repo.exists_by_id.return_value = False

    service = ReportService(repo)
    with pytest.raises(ReportNotFoundException):
        await service.delete(uuid4())
