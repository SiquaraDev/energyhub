"""Router REST do módulo `clients` (CRUD + listagem paginada)."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.clients.application.dto.client_request_dto import ClientRequestDTO
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.dto.contact_request_dto import ContactRequestDTO
from energyhub.clients.application.dto.contact_response_dto import ContactResponseDTO
from energyhub.clients.application.service.client_service import ClientService
from energyhub.clients.application.service.contact_service import ContactService
from energyhub.clients.application.usecase.create_client_use_case import CreateClientUseCase
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.clients.infrastructure.persistence.contact_repository import ContactRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.constant.permissions import (
    CLIENT_CREATE,
    CLIENT_DELETE,
    CLIENT_READ,
    CLIENT_UPDATE,
)
from energyhub.shared.infrastructure.persistence.database import get_session
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_client_service(session: AsyncSession = Depends(get_session)) -> ClientService:
    """Provedor do `ClientService` por requisição (repositório sobre a sessão)."""
    return ClientService(ClientRepository(session))


def get_create_client_use_case(
    service: ClientService = Depends(get_client_service),
) -> CreateClientUseCase:
    """Provedor do caso de uso de criação de cliente."""
    return CreateClientUseCase(service)


def get_contact_service(session: AsyncSession = Depends(get_session)) -> ContactService:
    """Provedor do `ContactService` por requisição."""
    return ContactService(ContactRepository(session), ClientRepository(session))


class ClientRouter(BaseRouter):
    """Registra os endpoints REST de clientes sob `/api/v1/clients`."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/clients",
            tags=["clients"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.post(
            "",
            response_model=ClientResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Cria um cliente",
            description="Cria um cliente (com contatos opcionais). Rejeita CNPJ duplicado.",
            dependencies=[Depends(require_permission(CLIENT_CREATE))],
        )
        async def create(
            dto: ClientRequestDTO,
            use_case: CreateClientUseCase = Depends(get_create_client_use_case),
        ) -> ClientResponseDTO:
            return await use_case.execute(dto)

        @router.get(
            "/{client_id}",
            response_model=ClientResponseDTO,
            summary="Busca um cliente por id",
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        async def find_by_id(
            client_id: UUID,
            service: ClientService = Depends(get_client_service),
        ) -> ClientResponseDTO:
            return await service.find_by_id(client_id)

        @router.get(
            "",
            response_model=PageResponse[ClientResponseDTO],
            summary="Lista clientes (paginado)",
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        async def find_all(
            service: ClientService = Depends(get_client_service),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            sort: str | None = Query(None, description="Campo de ordenação"),
            direction: str = Query("asc", pattern="^(asc|desc)$", description="Direção"),
        ) -> PageResponse[ClientResponseDTO]:
            return await service.find_all(
                PageRequest(page=page, size=size, sort=sort, direction=direction)
            )

        @router.put(
            "/{client_id}",
            response_model=ClientResponseDTO,
            summary="Atualiza um cliente",
            dependencies=[Depends(require_permission(CLIENT_UPDATE))],
        )
        async def update(
            client_id: UUID,
            dto: ClientRequestDTO,
            service: ClientService = Depends(get_client_service),
        ) -> ClientResponseDTO:
            return await service.update(client_id, dto)

        @router.delete(
            "/{client_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Remove um cliente",
            dependencies=[Depends(require_permission(CLIENT_DELETE))],
        )
        async def delete(
            client_id: UUID,
            service: ClientService = Depends(get_client_service),
        ) -> None:
            await service.delete(client_id)

        @router.post(
            "/{client_id}/contacts",
            response_model=ContactResponseDTO,
            status_code=status.HTTP_201_CREATED,
            summary="Adiciona um contato ao cliente",
            dependencies=[Depends(require_permission(CLIENT_UPDATE))],
        )
        async def add_contact(
            client_id: UUID,
            dto: ContactRequestDTO,
            service: ContactService = Depends(get_contact_service),
        ) -> ContactResponseDTO:
            return await service.create(client_id, dto)

        @router.get(
            "/{client_id}/contacts",
            response_model=list[ContactResponseDTO],
            summary="Lista os contatos do cliente",
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        async def list_contacts(
            client_id: UUID,
            service: ContactService = Depends(get_contact_service),
        ) -> list[ContactResponseDTO]:
            return await service.find_by_client_id(client_id)
