"""Exceção base da camada de aplicação."""


class ApplicationException(Exception):
    """Erro da camada de aplicação (orquestração de casos de uso)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message
