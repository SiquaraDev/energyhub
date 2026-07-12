"""DTO genérico de resposta paginada (Pydantic, serializável pela API)."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    """Página de resultados + metadados (zero-based).

    Use `PageResponse.create(...)` para calcular `total_pages`, `first` e `last`. É um modelo
    Pydantic para servir de `response_model` nos endpoints de listagem (Fase 6).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
