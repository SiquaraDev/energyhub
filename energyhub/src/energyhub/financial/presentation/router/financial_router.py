"""Router REST do módulo `financial` (CRUD de faturas + pagamentos como sub-recurso)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.financial.application.dto.invoice_request_dto import InvoiceRequestDTO
from energyhub.financial.application.dto.invoice_response_dto import InvoiceResponseDTO
from energyhub.financial.application.dto.payment_request_dto import PaymentRequestDTO
from energyhub.financial.application.dto.payment_response_dto import PaymentResponseDTO
from energyhub.financial.application.service.invoice_service import InvoiceService
from energyhub.financial.application.service.payment_service import PaymentService
from energyhub.financial.application.usecase.create_invoice_use_case import CreateInvoiceUseCase
from energyhub.financial.infrastructure.persistence.invoice_repository import InvoiceRepository
from energyhub.financial.infrastructure.persistence.payment_repository import PaymentRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.constant.permissions import (
    INVOICE_CREATE,
    INVOICE_DELETE,
    INVOICE_READ,
    INVOICE_UPDATE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_invoice_service(session: AsyncSession = Depends(get_session)) -> InvoiceService:
    """Provedor do `InvoiceService` por requisição (repositório sobre a sessão)."""
    return InvoiceService(InvoiceRepository(session))


def get_create_invoice_use_case(
    service: InvoiceService = Depends(get_invoice_service),
) -> CreateInvoiceUseCase:
    """Provedor do caso de uso de criação de fatura."""
    return CreateInvoiceUseCase(service)


def get_payment_service(session: AsyncSession = Depends(get_session)) -> PaymentService:
    """Provedor do `PaymentService` por requisição."""
    return PaymentService(PaymentRepository(session))


class FinancialRouter(BaseRouter):
    """Registra os endpoints REST de faturas e pagamentos sob `/api/v1/invoices`."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/invoices",
            tags=["financial"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=InvoiceResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria uma fatura",
            description="Cria uma fatura. Rejeita número de fatura duplicado.",
            dependencies=[Depends(require_permission(INVOICE_CREATE))],
        )
        async def create(
            dto: InvoiceRequestDTO,
            use_case: CreateInvoiceUseCase = Depends(get_create_invoice_use_case),
        ) -> InvoiceResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{invoice_id}",
            response_model=InvoiceResponseDTO,
            summary="Busca uma fatura por id",
            dependencies=[Depends(require_permission(INVOICE_READ))],
        )
        async def find_by_id(
            invoice_id: UUID,
            service: InvoiceService = Depends(get_invoice_service),
        ) -> InvoiceResponseDTO:
            return await service.find_by_id(invoice_id)

        @router.get(
            "",
            response_model=PageResponse[InvoiceResponseDTO],
            summary="Lista faturas (paginado)",
            dependencies=[Depends(require_permission(INVOICE_READ))],
        )
        async def find_all(
            service: InvoiceService = Depends(get_invoice_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[InvoiceResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{invoice_id}",
            response_model=InvoiceResponseDTO,
            summary="Atualiza uma fatura",
            dependencies=[Depends(require_permission(INVOICE_UPDATE))],
        )
        async def update(
            invoice_id: UUID,
            dto: InvoiceRequestDTO,
            service: InvoiceService = Depends(get_invoice_service),
        ) -> InvoiceResponseDTO:
            return await service.update(invoice_id, dto)

        @router.delete(
            "/{invoice_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove uma fatura",
            dependencies=[Depends(require_permission(INVOICE_DELETE))],
        )
        async def delete(
            invoice_id: UUID,
            service: InvoiceService = Depends(get_invoice_service),
        ) -> None:
            await service.delete(invoice_id)

        @router.post(
            "/{invoice_id}/payments",
            response_model=PaymentResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Registra um pagamento para a fatura",
            dependencies=[Depends(require_permission(INVOICE_UPDATE))],
        )
        async def add_payment(
            invoice_id: UUID,
            dto: PaymentRequestDTO,
            service: PaymentService = Depends(get_payment_service),
        ) -> PaymentResponseDTO:
            return await service.create(invoice_id, dto)

        @router.get(
            "/{invoice_id}/payments",
            response_model=list[PaymentResponseDTO],
            summary="Lista os pagamentos da fatura",
            dependencies=[Depends(require_permission(INVOICE_READ))],
        )
        async def list_payments(
            invoice_id: UUID,
            service: PaymentService = Depends(get_payment_service),
        ) -> list[PaymentResponseDTO]:
            return await service.find_by_invoice_id(invoice_id)
