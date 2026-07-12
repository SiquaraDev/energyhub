"""DTO de resposta de login (token de acesso + perfil do usuário autenticado)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from energyhub.auth.application.dto.user_response_dto import UserResponseDTO


class LoginResponseDTO(BaseModel):
    """Retorno do login: token JWT, tipo `bearer` e o perfil do usuário (sem senha)."""

    access_token: str = Field(
        ...,
        description="Token JWT de acesso a ser enviado no cabeçalho `Authorization: Bearer`",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.assinatura"],
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo do token de acesso (sempre `bearer`)",
        examples=["bearer"],
    )
    user: UserResponseDTO = Field(..., description="Perfil do usuário autenticado (sem a senha)")
