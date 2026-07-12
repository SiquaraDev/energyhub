"""Testes de componente do `ContractRouter` (serviços mockados; sem banco)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.contracts.application.dto.contract_response_dto import ContractResponseDTO
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.contracts.presentation.router.contract_router import (
    ContractRouter,
    get_contract_service,
    get_create_contract_use_case,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _contract_dto() -> ContractResponseDTO:
    return ContractResponseDTO(
        id=uuid4(),
        contract_number="CT-2026-001",
        client_id=uuid4(),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        energy_amount=Decimal("100.5"),
        unit_price=Decimal("250.00"),
        total_value=Decimal("25125.00"),
        type=ContractType.PURCHASE,
        status=ContractStatus.DRAFT,
    )


def _payload() -> dict[str, Any]:
    return {
        "contract_number": "CT-2026-001",
        "client_id": str(uuid4()),
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "energy_amount": "100.5",
        "unit_price": "250.00",
        "total_value": "25125.00",
        "type": "PURCHASE",
    }


def test_create_contract_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _contract_dto()
    api = router_client(
        ContractRouter().get_router(), {get_create_contract_use_case: lambda: use_case}
    )

    response = api.post("/api/v1/contracts", json=_payload())

    assert response.status_code == 201
    assert response.json()["contract_number"] == "CT-2026-001"


def test_get_contract_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _contract_dto()
    api = router_client(ContractRouter().get_router(), {get_contract_service: lambda: service})

    response = api.get(f"/api/v1/contracts/{uuid4()}")

    assert response.status_code == 200


def test_list_contracts_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_contract_dto()], 0, 20, 1)
    api = router_client(ContractRouter().get_router(), {get_contract_service: lambda: service})

    response = api.get("/api/v1/contracts")

    assert response.status_code == 200


def test_update_contract_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _contract_dto()
    api = router_client(ContractRouter().get_router(), {get_contract_service: lambda: service})

    response = api.put(f"/api/v1/contracts/{uuid4()}", json=_payload())

    assert response.status_code == 200


def test_delete_contract_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(ContractRouter().get_router(), {get_contract_service: lambda: service})

    response = api.delete(f"/api/v1/contracts/{uuid4()}")

    assert response.status_code == 204
