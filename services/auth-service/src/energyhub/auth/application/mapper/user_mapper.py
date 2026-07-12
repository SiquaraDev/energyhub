"""Mapper entre `User` e seus DTOs."""

from __future__ import annotations

from energyhub.auth.application.dto.user_request_dto import UserRequestDTO
from energyhub.auth.application.dto.user_response_dto import UserResponseDTO
from energyhub.auth.domain.entity.user import User


class UserMapper:
    """Ponto único de tradução entidade↔DTO para `User`.

    `to_entity` deixa a senha em texto puro (o `UserService` a substitui pelo hash) e os papéis
    são resolvidos no serviço. `to_response_dto` nunca expõe a senha (não é campo do DTO).
    """

    @staticmethod
    def to_entity(dto: UserRequestDTO) -> User:
        return User(
            username=dto.username,
            password=dto.password,
            email=dto.email,
            full_name=dto.full_name,
        )

    @staticmethod
    def to_response_dto(entity: User) -> UserResponseDTO:
        return UserResponseDTO.model_validate(entity)
