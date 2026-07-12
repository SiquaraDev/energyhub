"""Testes unitários de `PageRequest` (clamping) e `PageResponse` (cálculo de páginas)."""

from __future__ import annotations

from energyhub.shared.application.dto.page_request import PageRequest
from energyhub.shared.application.dto.page_response import PageResponse


def test_page_request_computes_offset_and_limit() -> None:
    page_request = PageRequest(page=2, size=10)
    assert page_request.get_offset() == 20
    assert page_request.get_limit() == 10


def test_page_request_clamps_invalid_values() -> None:
    assert PageRequest(page=-5, size=0).page == 0
    assert PageRequest(page=0, size=0).size == 20  # DEFAULT_PAGE_SIZE
    assert PageRequest(page=0, size=10_000).size == 100  # MAX_PAGE_SIZE
    assert PageRequest(page=0, size=10, direction="sideways").direction == "asc"


def test_page_response_create_computes_pagination_metadata() -> None:
    page = PageResponse.create(content=[1, 2], page=0, size=2, total_elements=5)
    assert page.total_pages == 3
    assert page.first is True
    assert page.last is False
    assert page.total_elements == 5


def test_page_response_last_page() -> None:
    page = PageResponse.create(content=[5], page=2, size=2, total_elements=5)
    assert page.first is False
    assert page.last is True


def test_page_response_empty() -> None:
    page = PageResponse.create(content=[], page=0, size=20, total_elements=0)
    assert page.total_pages == 0
    assert page.content == []
