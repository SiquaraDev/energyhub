"""Testes unitários dos utilitários compartilhados (datas, strings, validação)."""

from __future__ import annotations

from datetime import timedelta

from energyhub.shared.util.date_utils import is_past, to_iso, utcnow
from energyhub.shared.util.string_utils import is_blank, normalize_whitespace, only_digits
from energyhub.shared.util.validation_utils import (
    is_positive,
    is_valid_cnpj_length,
    is_valid_email,
)


def test_utcnow_is_timezone_aware() -> None:
    now = utcnow()
    assert now.tzinfo is not None


def test_to_iso_roundtrips() -> None:
    now = utcnow()
    assert to_iso(now) == now.isoformat()


def test_is_past_discriminates() -> None:
    assert is_past(utcnow() - timedelta(hours=1)) is True
    assert is_past(utcnow() + timedelta(hours=1)) is False


def test_is_blank() -> None:
    assert is_blank(None) is True
    assert is_blank("   ") is True
    assert is_blank("x") is False


def test_normalize_whitespace_collapses_runs() -> None:
    assert normalize_whitespace("  a   b\tc  ") == "a b c"


def test_only_digits_strips_non_digits() -> None:
    assert only_digits("a1-b2.c3") == "123"


def test_is_valid_email() -> None:
    assert is_valid_email("user@energyhub.local") is True
    assert is_valid_email("semarroba") is False


def test_is_valid_cnpj_length() -> None:
    assert is_valid_cnpj_length("11.222.333/0001-81") is True
    assert is_valid_cnpj_length("123") is False


def test_is_positive() -> None:
    assert is_positive(1.5) is True
    assert is_positive(0) is False
    assert is_positive(-2) is False
