"""Testes unitários dos validadores reutilizados pelos DTOs."""

from __future__ import annotations

import pytest

from energyhub.shared.application.validation.validators import (
    validate_cnpj,
    validate_email,
    validate_non_empty,
)


def test_validate_cnpj_returns_value_when_valid() -> None:
    assert validate_cnpj("11222333000181") == "11222333000181"


def test_validate_cnpj_raises_when_invalid() -> None:
    with pytest.raises(ValueError):
        validate_cnpj("123")


def test_validate_non_empty_returns_value() -> None:
    assert validate_non_empty("EnergyHub") == "EnergyHub"


@pytest.mark.parametrize("value", ["", "   "])
def test_validate_non_empty_raises_on_blank(value: str) -> None:
    with pytest.raises(ValueError):
        validate_non_empty(value)


def test_validate_email_returns_value_when_valid() -> None:
    assert validate_email("user@energyhub.local") == "user@energyhub.local"


@pytest.mark.parametrize("value", ["semarroba", "a@b", "@b.com"])
def test_validate_email_raises_when_invalid(value: str) -> None:
    with pytest.raises(ValueError):
        validate_email(value)
