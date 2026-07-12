"""Router base que encapsula o APIRouter do FastAPI."""

from fastapi import APIRouter


class BaseRouter:
    """Base para os routers dos módulos, padronizando prefixo e tags."""

    def __init__(self, prefix: str = "", tags: list[str] | None = None) -> None:
        # FastAPI tipa `tags` como list[str | Enum]; aqui só usamos str (list é invariante).
        self._router = APIRouter(prefix=prefix, tags=tags or [])  # type: ignore[arg-type]

    def get_router(self) -> APIRouter:
        """Retorna a instância de APIRouter para inclusão na aplicação."""
        return self._router
