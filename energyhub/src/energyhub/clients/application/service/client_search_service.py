"""Serviço de busca de clientes (Elasticsearch) — Fase 11.

Executa busca full-text relevância-ranqueada (`multi_match` com boosting + `fuzziness='AUTO'`),
filtro por localização e busca avançada (query `bool` composta a partir de um `SearchFilter`),
sempre paginando via `PageRequest`/`PageResponse` e mapeando os documentos em `ClientResponseDTO`.

Síncrono (cliente ES síncrono); os endpoints do router são declarados `def`, então o FastAPI os
executa num _threadpool_ (não bloqueiam o event loop).
"""

from __future__ import annotations

from typing import Any

from elasticsearch_dsl import Q

from energyhub.clients.application.dto.client_response_dto import ClientResponseDTO
from energyhub.clients.application.mapper.client_mapper import ClientMapper
from energyhub.clients.infrastructure.search.client_search_repository import ClientSearchRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse
from energyhub.shared.application.dto.search_filter import SearchFilter

# Campos do full-text com boosting: razão social pesa mais que fantasia; CNPJ como âncora exata.
_DEFAULT_FIELDS = ["corporate_name^2", "trade_name^1.5", "cnpj"]


class ClientSearchService:
    """Busca de clientes sobre o índice `clients`."""

    def __init__(
        self, repository: ClientSearchRepository, mapper: ClientMapper | None = None
    ) -> None:
        self._repository = repository
        self._mapper = mapper or ClientMapper()

    def _to_page(self, search: Any, page_request: PageRequest) -> PageResponse[ClientResponseDTO]:
        """Aplica offset/limit, executa e monta o `PageResponse` (total = hits.total.value)."""
        offset = page_request.get_offset()
        response = search[offset : offset + page_request.get_limit()].execute()
        content = [self._mapper.document_to_response_dto(hit) for hit in response]
        total = response.hits.total.value
        return PageResponse.create(content, page_request.page, page_request.size, total)

    def search(self, query: str, page_request: PageRequest) -> PageResponse[ClientResponseDTO]:
        """Full-text `multi_match` (boosting + fuzziness), ordenado por relevância e paginado."""
        search = self._repository.new_search().query(
            "multi_match", query=query, fields=_DEFAULT_FIELDS, fuzziness="AUTO"
        )
        return self._to_page(search, page_request)

    def filter_by_location(
        self, city: str, state: str, page_request: PageRequest
    ) -> PageResponse[ClientResponseDTO]:
        """Filtra por `city` E `state` (term keyword), paginado."""
        search = self._repository.new_search().query(
            "bool", filter=[Q("term", city=city), Q("term", state=state)]
        )
        return self._to_page(search, page_request)

    def advanced_search(
        self, search_filter: SearchFilter, page_request: PageRequest
    ) -> PageResponse[ClientResponseDTO]:
        """Query `bool`: `multi_match` opcional + condições `term`/`range` + `min_score`."""
        must: list[Any] = []
        if search_filter.query:
            multi_match: dict[str, Any] = {
                "query": search_filter.query,
                "fields": search_filter.fields or _DEFAULT_FIELDS,
            }
            if search_filter.fuzzy:
                multi_match["fuzziness"] = "AUTO"
            must.append(Q("multi_match", **multi_match))

        filters: list[Any] = []
        for condition in search_filter.conditions:
            if condition.operator == "eq":
                filters.append(Q("term", **{condition.field: condition.value}))
            else:  # gt / lt / gte / lte -> range
                filters.append(
                    Q("range", **{condition.field: {condition.operator: condition.value}})
                )

        search = self._repository.new_search().query("bool", must=must, filter=filters)
        if search_filter.min_score is not None:
            search = search.extra(min_score=search_filter.min_score)
        return self._to_page(search, page_request)
