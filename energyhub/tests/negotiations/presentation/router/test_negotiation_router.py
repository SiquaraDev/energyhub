"""Testes de componente do `NegotiationRouter` (negociações + transações; serviços mockados)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

from energyhub.negotiations.application.dto.energy_transaction_response_dto import (
    EnergyTransactionResponseDTO,
)
from energyhub.negotiations.application.dto.negotiation_response_dto import (
    NegotiationResponseDTO,
)
from energyhub.negotiations.domain.entity.negotiation_status import NegotiationStatus
from energyhub.negotiations.domain.entity.transaction_type import TransactionType
from energyhub.negotiations.presentation.router.negotiation_router import (
    NegotiationRouter,
    get_create_negotiation_use_case,
    get_energy_transaction_service,
    get_negotiation_service,
)
from energyhub.shared.application.dto.page_response import PageResponse


def _negotiation_dto() -> NegotiationResponseDTO:
    return NegotiationResponseDTO(id=uuid4(), contract_id=uuid4(), status=NegotiationStatus.DRAFT)


def _transaction_dto(negotiation_id: Any) -> EnergyTransactionResponseDTO:
    return EnergyTransactionResponseDTO(
        id=uuid4(),
        negotiation_id=negotiation_id,
        amount=Decimal("10.5"),
        price=Decimal("300.00"),
        type=TransactionType.BUY,
        transaction_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
    )


def test_create_negotiation_returns_201(router_client: Any) -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = _negotiation_dto()
    api = router_client(
        NegotiationRouter().get_router(), {get_create_negotiation_use_case: lambda: use_case}
    )

    response = api.post("/api/v1/negotiations", json={"contract_id": str(uuid4())})

    assert response.status_code == 201


def test_get_negotiation_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_by_id.return_value = _negotiation_dto()
    api = router_client(
        NegotiationRouter().get_router(), {get_negotiation_service: lambda: service}
    )

    response = api.get(f"/api/v1/negotiations/{uuid4()}")

    assert response.status_code == 200


def test_list_negotiations_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.find_all.return_value = PageResponse.create([_negotiation_dto()], 0, 20, 1)
    api = router_client(
        NegotiationRouter().get_router(), {get_negotiation_service: lambda: service}
    )

    response = api.get("/api/v1/negotiations")

    assert response.status_code == 200


def test_update_negotiation_returns_200(router_client: Any) -> None:
    service = AsyncMock()
    service.update.return_value = _negotiation_dto()
    api = router_client(
        NegotiationRouter().get_router(), {get_negotiation_service: lambda: service}
    )

    response = api.put(
        f"/api/v1/negotiations/{uuid4()}",
        json={"contract_id": str(uuid4()), "status": "IN_PROGRESS"},
    )

    assert response.status_code == 200


def test_delete_negotiation_returns_204(router_client: Any) -> None:
    service = AsyncMock()
    service.delete.return_value = None
    api = router_client(
        NegotiationRouter().get_router(), {get_negotiation_service: lambda: service}
    )

    response = api.delete(f"/api/v1/negotiations/{uuid4()}")

    assert response.status_code == 204


def test_add_transaction_returns_201(router_client: Any) -> None:
    negotiation_id = uuid4()
    service = AsyncMock()
    service.create.return_value = _transaction_dto(negotiation_id)
    api = router_client(
        NegotiationRouter().get_router(), {get_energy_transaction_service: lambda: service}
    )

    response = api.post(
        f"/api/v1/negotiations/{negotiation_id}/transactions",
        json={
            "amount": "10.5",
            "price": "300.00",
            "type": "BUY",
            "transaction_date": "2026-01-10T00:00:00Z",
        },
    )

    assert response.status_code == 201


def test_list_transactions_returns_200(router_client: Any) -> None:
    negotiation_id = uuid4()
    service = AsyncMock()
    service.find_by_negotiation_id.return_value = [_transaction_dto(negotiation_id)]
    api = router_client(
        NegotiationRouter().get_router(), {get_energy_transaction_service: lambda: service}
    )

    response = api.get(f"/api/v1/negotiations/{negotiation_id}/transactions")

    assert response.status_code == 200
    assert len(response.json()) == 1
