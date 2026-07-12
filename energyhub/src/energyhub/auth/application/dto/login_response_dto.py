"""DTO de resposta de login (token de acesso + perfil do usuário autenticado)."""

from __future__ import annotations

from pydantic import BaseModel

from energyhub.auth.application.dto.user_response_dto import UserResponseDTO


class LoginResponseDTO(BaseModel):
    """Retorno do login: token JWT, tipo `bearer` e o perfil do usuário (sem senha)."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO
