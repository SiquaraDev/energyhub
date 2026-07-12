"""Caso de uso: criar cliente."""

from __future__ import annotations

from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.service.client_service import ClientService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateClientUseCase(UseCase[ClientRequestDTO, ClientResponseDTO]):
    """Orquestra a criação de um cliente delegando ao `ClientService` (sem lógica própria)."""

    def __init__(self, service: ClientService) -> None:
        self._service = service

    async def execute(self, input_data: ClientRequestDTO) -> ClientResponseDTO:
        return await self._service.create(input_data)
