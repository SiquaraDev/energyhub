"""DTO de requisição de login (credenciais em texto puro)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequestDTO(BaseModel):
    """Credenciais enviadas ao endpoint de login."""

    username: str = Field(..., min_length=1, description="Nome de usuário")
    password: str = Field(..., min_length=1, description="Senha em texto puro")
