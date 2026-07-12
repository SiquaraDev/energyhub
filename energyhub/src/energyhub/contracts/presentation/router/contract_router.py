"""Router REST do módulo `contracts` (CRUD + listagem paginada)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.contracts.application.dto.contract_request_dto import ContractRequestDTO
from energyhub.contracts.application.dto.contract_response_dto import ContractResponseDTO
from energyhub.contracts.application.service.contract_service import ContractService
from energyhub.contracts.application.usecase.create_contract_use_case import CreateContractUseCase
from energyhub.contracts.infrastructure.persistence.contract_repository import ContractRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_contract_service(session: AsyncSession = Depends(get_session)) -> ContractService:
    """Provedor do `ContractService` por requisição (repositório sobre a sessão)."""
    return ContractService(ContractRepository(session))


def get_create_contract_use_case(
    service: ContractService = Depends(get_contract_service),
) -> CreateContractUseCase:
    """Provedor do caso de uso de criação de contrato."""
    return CreateContractUseCase(service)


class ContractRouter(BaseRouter):
    """Registra os endpoints REST de contratos sob `/api/v1/contracts`."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/contracts", tags=["contracts"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=ContractResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria um contrato",
            description="Cria um contrato de energia. Rejeita número de contrato duplicado.",
        )
        async def create(
            dto: ContractRequestDTO,
            use_case: CreateContractUseCase = Depends(get_create_contract_use_case),
        ) -> ContractResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{contract_id}",
            response_model=ContractResponseDTO,
            summary="Busca um contrato por id",
        )
        async def find_by_id(
            contract_id: UUID,
            service: ContractService = Depends(get_contract_service),
        ) -> ContractResponseDTO:
            return await service.find_by_id(contract_id)

        @router.get(
            "",
            response_model=PageResponse[ContractResponseDTO],
            summary="Lista contratos (paginado)",
        )
        async def find_all(
            service: ContractService = Depends(get_contract_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[ContractResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{contract_id}",
            response_model=ContractResponseDTO,
            summary="Atualiza um contrato",
        )
        async def update(
            contract_id: UUID,
            dto: ContractRequestDTO,
            service: ContractService = Depends(get_contract_service),
        ) -> ContractResponseDTO:
            return await service.update(contract_id, dto)

        @router.delete(
            "/{contract_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove um contrato",
        )
        async def delete(
            contract_id: UUID,
            service: ContractService = Depends(get_contract_service),
        ) -> None:
            await service.delete(contract_id)
