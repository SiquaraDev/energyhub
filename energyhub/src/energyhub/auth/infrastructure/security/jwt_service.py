"""Serviço de emissão e validação de tokens JWT (HS256) — Fase 7.

Lê a configuração de assinatura de `energyhub.config.settings` (`secret_key`, `algorithm`,
`access_token_expire_minutes`). Emite tokens de acesso *stateless* carregando `sub` (username) e
`exp`, e oferece decodificação/validação tolerante a falhas (retorna `None`/`False` em vez de
propagar exceções da lib para o chamador).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from energyhub.config.settings import settings


class JwtService:
    """Cria, decodifica e valida tokens JWT assinados com o segredo da aplicação."""

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str | None = None,
        access_token_expire_minutes: int | None = None,
    ) -> None:
        self._secret_key = secret_key or settings.secret_key
        self._algorithm = algorithm or settings.algorithm
        self._expire_minutes = (
            access_token_expire_minutes
            if access_token_expire_minutes is not None
            else settings.access_token_expire_minutes
        )

    def create_token(self, subject: str, claims: dict[str, Any] | None = None) -> str:
        """Emite um JWT assinado com `sub`, `exp` (agora + expiração) e claims adicionais."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        payload: dict[str, Any] = {**(claims or {}), "sub": subject, "exp": expire}
        token: str = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return token

    def decode_token(self, token: str) -> dict[str, Any] | None:
        """Decodifica e valida (assinatura + expiração) o token; `None` se inválido/malformado."""
        try:
            payload: dict[str, Any] = jwt.decode(
                token, self._secret_key, algorithms=[self._algorithm]
            )
            return payload
        except JWTError:
            return None

    def extract_username(self, token: str) -> str | None:
        """Retorna o `sub` (username) de um token válido, ou `None` se inválido."""
        payload = self.decode_token(token)
        if payload is None:
            return None
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None

    def is_token_valid(self, token: str) -> bool:
        """`True` se o token é assinado por este serviço e não expirou; `False` caso contrário."""
        return self.decode_token(token) is not None
