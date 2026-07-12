"""DTO de requisição de página (paginação por offset/limit, zero-based)."""

from __future__ import annotations

from dataclasses import dataclass

from energyhub.shared.constant.application_constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


@dataclass
class PageRequest:
    """Parâmetros de paginação/ordenação. Páginas são **zero-based** (`page=0` é a primeira).

    `size` é limitado a `[1, MAX_PAGE_SIZE]` para evitar leituras não-limitadas.
    """

    page: int = 0
    size: int = DEFAULT_PAGE_SIZE
    sort: str | None = None
    direction: str = "asc"

    def __post_init__(self) -> None:
        if self.page < 0:
            self.page = 0
        if self.size < 1:
            self.size = DEFAULT_PAGE_SIZE
        if self.size > MAX_PAGE_SIZE:
            self.size = MAX_PAGE_SIZE
        if self.direction.lower() not in ("asc", "desc"):
            self.direction = "asc"

    def get_offset(self) -> int:
        """Deslocamento inicial (`page * size`)."""
        return self.page * self.size

    def get_limit(self) -> int:
        """Quantidade máxima de itens da página (`size`)."""
        return self.size
