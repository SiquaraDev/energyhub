"""Testes unitários da entidade `Contract` (validação + transições de status)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from energyhub.contracts.domain.entity.contract import Contract
from energyhub.contracts.domain.entity.contract_status import ContractStatus
from energyhub.contracts.domain.entity.contract_type import ContractType
from energyhub.contracts.domain.exception.invalid_contract_status_exception import (
    InvalidContractStatusException,
)
from energyhub.shared.domain.exception.validation_exception import ValidationException


def _contract(**overrides: object) -> Contract:
    data: dict[str, object] = {
        "contract_number": "CT-1",
        "client_id": uuid4(),
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
        "energy_amount": Decimal("100"),
        "unit_price": Decimal("10"),
        "total_value": Decimal("1000"),
        "type": ContractType.PURCHASE,
    }
    data.update(overrides)
    return Contract(**data)


def test_valid_contract_constructs() -> None:
    assert _contract().status == ContractStatus.DRAFT


def test_rejects_blank_contract_number() -> None:
    with pytest.raises(ValidationException):
        _contract(contract_number="   ")


def test_rejects_end_date_not_after_start_date() -> None:
    with pytest.raises(ValidationException):
        _contract(start_date=date(2026, 12, 31), end_date=date(2026, 1, 1))


@pytest.mark.parametrize("field", ["energy_amount", "unit_price", "total_value"])
def test_rejects_non_positive_amounts(field: str) -> None:
    with pytest.raises(ValidationException):
        _contract(**{field: Decimal("0")})


def test_approve_from_pending_approval() -> None:
    contract = _contract(status=ContractStatus.PENDING_APPROVAL)
    contract.approve()
    assert contract.status == ContractStatus.APPROVED


def test_approve_from_wrong_status_raises() -> None:
    contract = _contract(status=ContractStatus.DRAFT)
    with pytest.raises(InvalidContractStatusException):
        contract.approve()


def test_activate_from_approved_with_started_date() -> None:
    contract = _contract(
        status=ContractStatus.APPROVED,
        start_date=date.today() - timedelta(days=1),
        end_date=date.today() + timedelta(days=365),
    )
    contract.activate()
    assert contract.status == ContractStatus.ACTIVE


def test_activate_from_wrong_status_raises() -> None:
    contract = _contract(status=ContractStatus.DRAFT)
    with pytest.raises(InvalidContractStatusException):
        contract.activate()
