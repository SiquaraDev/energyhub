"""Testes de integração da camada de persistência (CRUD, finders, filtros, paginação).

Rodam contra o PostgreSQL do docker-compose (schema da Fase 4). Cada teste é isolado por
rollback da sessão (ver a fixture `session` em `conftest.py`).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from energyhub.clients.application.dto.client_filter_dto import ClientFilterDTO
from energyhub.clients.domain.entity.client import Client
from energyhub.clients.infrastructure.persistence.client_repository import ClientRepository
from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


async def test_save_client_generates_id_and_persists(session: AsyncSession) -> None:
    repo = ClientRepository(session)
    client = Client(
        cnpj="11222333000181",
        corporate_name="Usina Alpha",
        city="Sao Paulo",
        state="SP",
    )
    saved = await repo.save(client)

    assert saved.id is not None
    fetched = await repo.find_by_id(saved.id)
    assert fetched is not None
    assert fetched.cnpj == "11222333000181"
    assert fetched.corporate_name == "Usina Alpha"
    assert fetched.active is True


async def test_find_by_cnpj(session: AsyncSession) -> None:
    repo = ClientRepository(session)
    await repo.save(Client(cnpj="11444777000161", corporate_name="Usina Beta"))

    found = await repo.find_by_cnpj("11444777000161")
    assert found is not None
    assert found.corporate_name == "Usina Beta"
    assert await repo.exists_by_cnpj("11444777000161") is True
    assert await repo.find_by_cnpj("99999999999999") is None


async def test_filter_and_pagination(session: AsyncSession) -> None:
    repo = ClientRepository(session)
    for i in range(5):
        await repo.save(
            Client(
                cnpj=f"112223330{i:05d}",
                corporate_name=f"Cliente {i}",
                city="Rio de Janeiro",
                active=(i % 2 == 0),
            )
        )

    # Filtro: cidade + ativo → i em {0, 2, 4}.
    active_in_rio = await repo.search(ClientFilterDTO(city="Rio de Janeiro", active=True))
    assert len(active_in_rio) == 3

    # Paginação: tamanho de página limitado + total correto.
    page_request = PageRequest(page=0, size=2)
    content, total = await repo.find_page(page_request.get_offset(), page_request.get_limit())
    assert total == 5
    assert len(content) == 2  # page size limita o conteúdo

    page: PageResponse[Client] = PageResponse.create(
        content, page_request.page, page_request.size, total
    )
    assert page.total_pages == 3
    assert page.first is True
    assert page.last is False


async def test_max_page_size_is_bounded() -> None:
    # size acima do máximo é limitado (sem tocar no banco).
    page_request = PageRequest(page=0, size=10_000)
    assert page_request.get_limit() == 100  # MAX_PAGE_SIZE
