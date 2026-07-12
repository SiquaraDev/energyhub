"""Caso de uso: criar negociação."""

from __future__ import annotations

from energyhub.negotiations.application.dto.negotiation_request_dto import NegotiationRequestDTO
from energyhub.negotiations.application.dto.negotiation_response_dto import NegotiationResponseDTO
from energyhub.negotiations.application.service.negotiation_service import NegotiationService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateNegotiationUseCase(UseCase[NegotiationRequestDTO, NegotiationResponseDTO]):
    """Orquestra a criação de uma negociação delegando ao `NegotiationService`."""

    def __init__(self, service: NegotiationService) -> None:
        self._service = service

    async def execute(self, input_data: NegotiationRequestDTO) -> NegotiationResponseDTO:
        return await self._service.create(input_data)
