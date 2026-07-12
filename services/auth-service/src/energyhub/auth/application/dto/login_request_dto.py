"""DTO de requisição de login (credenciais em texto puro)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequestDTO(BaseModel):
    """Credenciais enviadas ao endpoint de login."""

    username: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nome de usuário",
        examples=["operador01"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=72,
        description="Senha em texto puro",
        examples=["SenhaForte123!"],
    )
