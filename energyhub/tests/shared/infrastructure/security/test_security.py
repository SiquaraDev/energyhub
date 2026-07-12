"""Testes unitários de hashing de senha (bcrypt) e emissão/verificação de JWT."""

from __future__ import annotations

from energyhub.auth.infrastructure.security.jwt_service import JwtService
from energyhub.shared.infrastructure.security.password_hasher import (
    get_password_hash,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = get_password_hash("segredo123")
    assert hashed != "segredo123"
    assert verify_password("segredo123", hashed) is True
    assert verify_password("errada", hashed) is False


def test_jwt_create_and_decode() -> None:
    service = JwtService()
    token = service.create_token("admin")

    assert isinstance(token, str)
    payload = service.decode_token(token)
    assert payload is not None
    assert payload["sub"] == "admin"
    assert service.extract_username(token) == "admin"
    assert service.is_token_valid(token) is True


def test_jwt_rejects_garbage_token() -> None:
    service = JwtService()
    assert service.decode_token("not-a-jwt") is None
    assert service.extract_username("not-a-jwt") is None
    assert service.is_token_valid("not-a-jwt") is False


def test_jwt_carries_extra_claims() -> None:
    service = JwtService()
    token = service.create_token("admin", claims={"role": "ADMIN"})
    payload = service.decode_token(token)
    assert payload is not None
    assert payload["role"] == "ADMIN"
