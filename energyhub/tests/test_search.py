"""Testes do subsistema de busca (Elasticsearch · Fase 11).

Cobrem: bootstrap idempotente de índices, full-text com boosting/fuzziness, filtro por localização,
busca avançada (term/range + min_score), paginação e o **orçamento de latência**. Precisam apenas do
Elasticsearch (não do Postgres); pulam automaticamente se o cluster estiver indisponível.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Iterator

import pytest

from energyhub.clients.application.service.client_search_service import ClientSearchService
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.infrastructure.search.client_document import ClientDocument
from energyhub.clients.infrastructure.search.client_search_repository import ClientSearchRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.search_filter import FilterCondition, SearchFilter
from energyhub.shared.infrastructure.search.elasticsearch_config import ElasticsearchConfig

LATENCY_BUDGET_SECONDS = 1.0
INDEX = ClientDocument.Index.name


def _make_client(run: str, i: int, city: str, state: str) -> Client:
    return Client(
        cnpj=f"{run[:8]}{i:06d}",
        corporate_name=f"Usina {run} numero {i}",
        trade_name=f"Fantasia {run}",
        city=city,
        state=state,
        active=True,
    )


@pytest.fixture(scope="module")
def search_env() -> Iterator[tuple[ClientSearchService, str, list[str]]]:
    """Índice populado com clientes de teste; pula se o Elasticsearch não responder."""
    client = ElasticsearchConfig.get_client()
    try:
        if not client.ping():
            pytest.skip("Elasticsearch indisponível")
    except Exception:  # noqa: BLE001
        pytest.skip("Elasticsearch indisponível")

    ElasticsearchConfig.create_indices([ClientDocument])  # idempotente

    run = uuid.uuid4().hex[:8]
    repository = ClientSearchRepository(client)
    ids: list[str] = []
    # 5 em Campinas/ZZ + 1 em Santos/ZZ (para o filtro de localização discriminar a cidade).
    fixtures = [(i, "Campinas", "ZZ") for i in range(5)] + [(5, "Santos", "ZZ")]
    for i, city, state in fixtures:
        entity = _make_client(run, i, city, state)
        document = ClientDocument.from_entity(entity)
        repository.save(document)
        ids.append(str(entity.id))
    client.indices.refresh(index=INDEX)

    service = ClientSearchService(repository)
    yield service, run, ids

    for doc_id in ids:
        repository.delete(doc_id)
    client.indices.refresh(index=INDEX)


def test_search_full_text_returns_results_within_budget(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """Full-text relevância-ranqueada retorna resultados dentro do orçamento de latência (8.2)."""
    service, run, _ = search_env
    start = time.perf_counter()
    page = service.search(f"Usina {run}", PageRequest(page=0, size=10))
    elapsed = time.perf_counter() - start
    assert elapsed < LATENCY_BUDGET_SECONDS, f"busca levou {elapsed:.3f}s"
    assert page.total_elements >= 6
    assert page.content
    assert all(run in dto.corporate_name for dto in page.content)


def test_search_is_typo_tolerant(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """`fuzziness='AUTO'` casa mesmo com pequeno erro de digitação (9.2)."""
    service, run, _ = search_env
    page = service.search(f"Usna {run}", PageRequest(page=0, size=10))  # "Usna" (typo)
    assert page.total_elements >= 1


def test_location_filter(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """Filtro por cidade+estado retorna só quem casa em ambos (9.2)."""
    service, _, _ = search_env
    page = service.filter_by_location("Campinas", "ZZ", PageRequest(page=0, size=50))
    assert page.total_elements == 5
    assert all(dto.city == "Campinas" and dto.state == "ZZ" for dto in page.content)


def test_pagination(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """Paginação: `size` limita o conteúdo; `total_elements` = total de hits (9.3)."""
    service, run, _ = search_env
    page = service.search(f"Usina {run}", PageRequest(page=0, size=2))
    assert len(page.content) == 2
    assert page.total_elements >= 6
    assert page.size == 2
    assert page.first is True
    assert page.last is False


def test_advanced_search_term_and_range(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """Busca avançada: `eq`→term + `gte`→range compõem com o texto (9.2)."""
    service, run, _ = search_env
    search_filter = SearchFilter(
        query=f"Usina {run}",
        conditions=[
            FilterCondition(field="state", operator="eq", value="ZZ"),
            FilterCondition(field="created_at", operator="gte", value="2000-01-01"),
        ],
    )
    page = service.advanced_search(search_filter, PageRequest(page=0, size=50))
    assert page.total_elements == 6
    assert all(dto.state == "ZZ" for dto in page.content)


def test_advanced_search_min_score_excludes_low_relevance(
    search_env: tuple[ClientSearchService, str, list[str]],
) -> None:
    """`min_score` alto exclui resultados de baixa relevância (9.3)."""
    service, run, _ = search_env
    base = service.advanced_search(SearchFilter(query=f"Usina {run}"), PageRequest(page=0, size=50))
    filtered = service.advanced_search(
        SearchFilter(query=f"Usina {run}", min_score=1_000_000.0), PageRequest(page=0, size=50)
    )
    assert base.total_elements >= 6
    assert filtered.total_elements == 0
