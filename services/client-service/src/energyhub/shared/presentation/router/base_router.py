"""Router base que encapsula o APIRouter do FastAPI."""

from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter


class BaseRouter:
    """Base para os routers dos módulos, padronizando prefixo, tags e dependências de grupo."""

    def __init__(
        self,
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: Sequence[Any] | None = None,
    ) -> None:
        # FastAPI tipa `tags`/`dependencies` de forma mais específica; aqui passamos direto.
        self._router = APIRouter(
            prefix=prefix,
            tags=tags or [],  # type: ignore[arg-type]
            dependencies=dependencies or [],
        )

    def get_router(self) -> APIRouter:
        """Retorna a instância de APIRouter para inclusão na aplicação."""
        return self._router
