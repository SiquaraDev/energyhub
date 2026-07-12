"""Caso de uso: criar usuário."""

from __future__ import annotations

from energyhub.auth.application.dto.user_request_dto import UserRequestDTO
from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.application.service.user_service import UserService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateUserUseCase(UseCase[UserRequestDTO, UserResponseDTO]):
    """Orquestra a criação de um usuário delegando ao `UserService`."""

    def __init__(self, service: UserService) -> None:
        self._service = service

    async def execute(self, input_data: UserRequestDTO) -> UserResponseDTO:
        return await self._service.create(input_data)
