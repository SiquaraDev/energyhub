"""Caso de uso: criar contrato."""

from __future__ import annotations

from energyhub.contracts.application.dto.contract_request_dto import ContractRequestDTO
from energyhub.contracts.application.dto.contract_response_dto import ContractResponseDTO
from energyhub.contracts.application.service.contract_service import ContractService
from energyhub.shared.application.usecase.usecase import UseCase


class CreateContractUseCase(UseCase[ContractRequestDTO, ContractResponseDTO]):
    """Orquestra a criação de um contrato delegando ao `ContractService` (sem lógica própria)."""

    def __init__(self, service: ContractService) -> None:
        self._service = service

    async def execute(self, input_data: ContractRequestDTO) -> ContractResponseDTO:
        return await self._service.create(input_data)
