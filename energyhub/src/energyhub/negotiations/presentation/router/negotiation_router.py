"""Router REST do módulo `negotiations` (CRUD + listagem paginada + transações)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.negotiations.application.dto.energy_transaction_request_dto import (
    EnergyTransactionRequestDTO,
)
from energyhub.negotiations.application.dto.energy_transaction_response_dto import (
    EnergyTransactionResponseDTO,
)
from energyhub.negotiations.application.dto.negotiation_request_dto import NegotiationRequestDTO
from energyhub.negotiations.application.dto.negotiation_response_dto import NegotiationResponseDTO
from energyhub.negotiations.application.service.energy_transaction_service import (
    EnergyTransactionService,
)
from energyhub.negotiations.application.service.negotiation_service import NegotiationService
from energyhub.negotiations.application.usecase.create_negotiation_use_case import (
    CreateNegotiationUseCase,
)
from energyhub.negotiations.infrastructure.persistence.energy_transaction_repository import (
    EnergyTransactionRepository,
)
from energyhub.negotiations.infrastructure.persistence.negotiation_repository import (
    NegotiationRepository,
)
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_negotiation_service(session: AsyncSession = Depends(get_session)) -> NegotiationService:
    """Provedor do `NegotiationService` por requisição (repositório sobre a sessão)."""
    return NegotiationService(NegotiationRepository(session))


def get_create_negotiation_use_case(
    service: NegotiationService = Depends(get_negotiation_service),
) -> CreateNegotiationUseCase:
    """Provedor do caso de uso de criação de negociação."""
    return CreateNegotiationUseCase(service)


def get_energy_transaction_service(
    session: AsyncSession = Depends(get_session),
) -> EnergyTransactionService:
    """Provedor do `EnergyTransactionService` por requisição."""
    return EnergyTransactionService(EnergyTransactionRepository(session))


class NegotiationRouter(BaseRouter):
    """Registra os endpoints REST de negociações sob `/api/v1/negotiations`."""

    def __init__(self) -> None:
        super().__init__(prefix=f"{API_V1_PREFIX}/negotiations", tags=["negotiations"])
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=NegotiationResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria uma negociação",
        )
        async def create(
            dto: NegotiationRequestDTO,
            use_case: CreateNegotiationUseCase = Depends(get_create_negotiation_use_case),
        ) -> NegotiationResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{negotiation_id}",
            response_model=NegotiationResponseDTO,
            summary="Busca uma negociação por id",
        )
        async def find_by_id(
            negotiation_id: UUID,
            service: NegotiationService = Depends(get_negotiation_service),
        ) -> NegotiationResponseDTO:
            return await service.find_by_id(negotiation_id)

        @router.get(
            "",
            response_model=PageResponse[NegotiationResponseDTO],
            summary="Lista negociações (paginado)",
        )
        async def find_all(
            service: NegotiationService = Depends(get_negotiation_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[NegotiationResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{negotiation_id}",
            response_model=NegotiationResponseDTO,
            summary="Atualiza o status de uma negociação",
        )
        async def update(
            negotiation_id: UUID,
            dto: NegotiationRequestDTO,
            service: NegotiationService = Depends(get_negotiation_service),
        ) -> NegotiationResponseDTO:
            return await service.update(negotiation_id, dto)

        @router.delete(
            "/{negotiation_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove uma negociação",
        )
        async def delete(
            negotiation_id: UUID,
            service: NegotiationService = Depends(get_negotiation_service),
        ) -> None:
            await service.delete(negotiation_id)

        @router.post(
            "/{negotiation_id}/transactions",
            response_model=EnergyTransactionResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria uma transação de energia na negociação",
        )
        async def create_transaction(
            negotiation_id: UUID,
            dto: EnergyTransactionRequestDTO,
            service: EnergyTransactionService = Depends(get_energy_transaction_service),
        ) -> EnergyTransactionResponseDTO:
            return await service.create(negotiation_id, dto)

        @router.get(
            "/{negotiation_id}/transactions",
            response_model=list[EnergyTransactionResponseDTO],
            summary="Lista as transações de energia da negociação",
        )
        async def list_transactions(
            negotiation_id: UUID,
            service: EnergyTransactionService = Depends(get_energy_transaction_service),
        ) -> list[EnergyTransactionResponseDTO]:
            return await service.find_by_negotiation_id(negotiation_id)
