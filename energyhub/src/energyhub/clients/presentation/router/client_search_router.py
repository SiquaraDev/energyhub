"""Router REST de busca de clientes (Elasticsearch) — Fase 11.

Expõe busca full-text (`GET /`), filtro por localização (`GET /location`) e busca avançada
(`POST /advanced`) sob `/api/v1/search/clients` (prefixo próprio para não colidir com
`/api/v1/clients/{id}`). Endpoints síncronos → o FastAPI os roda num _threadpool_.
"""

from __future__ import annotations

from fastapi import Depends, Query

from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.service.client_search_service import ClientSearchService
from energyhub.clients.infrastructure.search.client_search_repository import ClientSearchRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.application.dto.search_filter import SearchFilter
from energyhub.shared.constant.application_constants import (
    API_V1_PREFIX,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
from energyhub.shared.constant.permissions import CLIENT_READ
from energyhub.shared.infrastructure.search.elasticsearch_config import ElasticsearchConfig
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.response.openapi_responses import AUTH_ERRORS
from energyhub.shared.presentation.router.base_router import BaseRouter


def get_client_search_service() -> ClientSearchService:
    """Provedor do `ClientSearchService` (repositório sobre o cliente ES compartilhado)."""
    return ClientSearchService(ClientSearchRepository(ElasticsearchConfig.get_client()))


class ClientSearchRouter(BaseRouter):
    """Registra os endpoints de busca de clientes sob `/api/v1/search/clients`."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/search/clients",
            tags=["Search"],
            dependencies=[Depends(get_current_user)],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.get(
            "",
            response_model=PageResponse[ClientResponseDTO],
            summary="Busca full-text de clientes",
            description=(
                "Busca por relevância (`multi_match` com boosting + `fuzziness='AUTO'`) sobre "
                "razão social, nome fantasia e CNPJ. Tolerante a erros de digitação."
            ),
            responses={**AUTH_ERRORS},
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        def full_text_search(
            q: str = Query(..., min_length=1, description="Texto da busca"),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            service: ClientSearchService = Depends(get_client_search_service),
        ) -> PageResponse[ClientResponseDTO]:
            return service.search(q, PageRequest(page=page, size=size))

        @router.get(
            "/location",
            response_model=PageResponse[ClientResponseDTO],
            summary="Filtra clientes por cidade/estado",
            description="Filtra por `city` e `state` (casamento exato), paginado.",
            responses={**AUTH_ERRORS},
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        def location_filter(
            city: str = Query(..., min_length=1, description="Cidade"),
            state: str = Query(..., min_length=1, description="UF/estado"),
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            service: ClientSearchService = Depends(get_client_search_service),
        ) -> PageResponse[ClientResponseDTO]:
            return service.filter_by_location(city, state, PageRequest(page=page, size=size))

        @router.post(
            "/advanced",
            response_model=PageResponse[ClientResponseDTO],
            summary="Busca avançada de clientes",
            description=(
                "Query `bool` composta: `multi_match` opcional + condições `term`/`range` "
                "(operadores eq/gt/lt/gte/lte) + `min_score` opcional."
            ),
            responses={**AUTH_ERRORS},
            dependencies=[Depends(require_permission(CLIENT_READ))],
        )
        def advanced_search(
            search_filter: SearchFilter,
            page: int = Query(0, ge=0, description="Página (zero-based)"),
            size: int = Query(
                DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Tamanho da página"
            ),
            service: ClientSearchService = Depends(get_client_search_service),
        ) -> PageResponse[ClientResponseDTO]:
            return service.advanced_search(search_filter, PageRequest(page=page, size=size))
