"""DTO genérico de resposta paginada."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PageResponse(Generic[T]):
    """Página de resultados + metadados (zero-based).

    Use `PageResponse.create(...)` para calcular `total_pages`, `first` e `last`.
    """

    content: list[T]
    page: int
    size: int
    total_elements: int
    total_pages: int
    first: bool
    last: bool

    @classmethod
    def create(cls, content: list[T], page: int, size: int, total_elements: int) -> PageResponse[T]:
        """Monta a resposta calculando `total_pages`, `first` e `last`."""
        total_pages = (total_elements + size - 1) // size if size > 0 else 0
        return cls(
            content=content,
            page=page,
            size=size,
            total_elements=total_elements,
            total_pages=total_pages,
            first=page <= 0,
            last=page >= total_pages - 1,
        )
