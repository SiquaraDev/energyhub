"""Testes unitários dos value objects (validação e normalização)."""

from __future__ import annotations

from decimal import Decimal

import pytest

from energyhub.shared.domain.valueobject.address import Address
from energyhub.shared.domain.valueobject.cnpj import CNPJ
from energyhub.shared.domain.valueobject.email import Email
from energyhub.shared.domain.valueobject.money import Money
from energyhub.shared.domain.valueobject.percentage import Percentage
from energyhub.shared.domain.valueobject.phone_number import PhoneNumber


def test_should_accept_valid_cnpj_and_normalize_digits() -> None:
    assert CNPJ("11222333000181").value == "11222333000181"
    assert CNPJ("11.222.333/0001-81").value == "11222333000181"


def test_should_format_cnpj() -> None:
    assert CNPJ("11222333000181").formatted() == "11.222.333/0001-81"


@pytest.mark.parametrize("value", ["00000000000000", "123", "11222333000180"])
def test_should_reject_invalid_cnpj(value: str) -> None:
    with pytest.raises(ValueError):
        CNPJ(value)


def test_should_accept_valid_email_and_lowercase_it() -> None:
    assert Email("Admin@EnergyHub.LOCAL").value == "admin@energyhub.local"


def test_should_reject_email_without_at_sign() -> None:
    with pytest.raises(ValueError):
        Email("invalido")


def test_money_defaults_to_brl() -> None:
    money = Money(Decimal("10.00"))
    assert money.amount == Decimal("10.00")
    assert money.currency == "BRL"


@pytest.mark.parametrize("value", ["0", "50", "100"])
def test_percentage_accepts_boundaries(value: str) -> None:
    assert Percentage(Decimal(value)).value == Decimal(value)


@pytest.mark.parametrize("value", ["-1", "101"])
def test_percentage_rejects_out_of_range(value: str) -> None:
    with pytest.raises(ValueError):
        Percentage(Decimal(value))


def test_phone_number_keeps_only_digits() -> None:
    assert PhoneNumber("(11) 99999-8888").value == "11999998888"


@pytest.mark.parametrize("value", ["123", "12345678901234"])
def test_phone_number_rejects_invalid_length(value: str) -> None:
    with pytest.raises(ValueError):
        PhoneNumber(value)


def test_address_defaults_country_to_brasil() -> None:
    address = Address(street="Rua A", city="São Paulo", state="SP", zip_code="01000-000")
    assert address.country == "Brasil"
