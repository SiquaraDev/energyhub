"""Exceção base do domínio."""


class DomainException(Exception):
    """Erro de domínio. Raiz da hierarquia de exceções de regras de negócio."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message
