"""Exceção base do domínio."""

from __future__ import annotations

from typing import ClassVar


class DomainException(Exception):
    """Erro de domínio. Raiz da hierarquia de exceções de regras de negócio.

    Cada subclasse expõe um `error_code` estável (legível por máquina), catalogado em
    `docs/API_ERRORS.md`, além da mensagem legível. O código default é `DOMAIN_ERROR`.
    """

    error_code: ClassVar[str] = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message
