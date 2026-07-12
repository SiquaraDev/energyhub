"""Serviço de autenticação: valida credenciais e emite o token de acesso (Fase 7)."""

from __future__ import annotations

from energyhub.auth.application.dto.login_request_dto import LoginRequestDTO
from energyhub.auth.application.dto.login_response_dto import LoginResponseDTO
from energyhub.auth.application.mapper.user_mapper import UserMapper
from energyhub.auth.domain.exception.invalid_credentials_exception import (
    InvalidCredentialsException,
)
from energyhub.auth.infrastructure.persistence.user_repository import UserRepository
from energyhub.auth.infrastructure.security.jwt_service import JwtService
from energyhub.shared.infrastructure.security.password_hasher import verify_password


class AuthenticationService:
    """Autentica um usuário por username/senha e devolve um `LoginResponseDTO` com o JWT."""

    def __init__(
        self,
        user_repository: UserRepository,
        jwt_service: JwtService | None = None,
        mapper: UserMapper | None = None,
    ) -> None:
        self._users = user_repository
        self._jwt = jwt_service or JwtService()
        self._mapper = mapper or UserMapper()

    async def login(self, dto: LoginRequestDTO) -> LoginResponseDTO:
        """Valida as credenciais e emite um token; rejeita usuário inexistente, senha errada
        ou conta inativa com o **mesmo** erro (não revela qual condição falhou)."""
        user = await self._users.find_by_username(dto.username)
        if user is None or not verify_password(dto.password, user.password) or not user.active:
            raise InvalidCredentialsException("Usuário ou senha inválidos")

        token = self._jwt.create_token(user.username)
        return LoginResponseDTO(access_token=token, user=self._mapper.to_response_dto(user))
