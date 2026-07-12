"""Modelo de resposta de erro padronizada da API."""

from dataclasses import dataclass


@dataclass
class ErrorResponse:
    """Corpo padronizado de erro retornado pela API."""

    timestamp: str
    status: int
    error: str
    message: str
    path: str
