"""Router de administração do cache (`/api/v1/cache`) — protegido por `CACHE_MANAGE` (Fase 9)."""

from __future__ import annotations

from fastapi import Depends
from fastapi_cache import FastAPICache

from energyhub.shared.constant.application_constants import API_V1_PREFIX
from energyhub.shared.constant.permissions import CACHE_MANAGE
from energyhub.shared.infrastructure.cache.cache_helper import invalidate_all_cache
from energyhub.shared.infrastructure.security.authorization import require_permission
from energyhub.shared.presentation.response.openapi_responses import AUTH_ERRORS
from energyhub.shared.presentation.router.base_router import BaseRouter


class CacheRouter(BaseRouter):
    """Endpoints de monitoramento e limpeza do cache — todos exigem a permissão `CACHE_MANAGE`."""

    def __init__(self) -> None:
        super().__init__(
            prefix=f"{API_V1_PREFIX}/cache",
            tags=["Cache"],
            dependencies=[Depends(require_permission(CACHE_MANAGE))],
        )
        self._register_routes()

    def _register_routes(self) -> None:
        router = self._router

        @router.get(
            "/stats",
            summary="Estatísticas do cache",
            description="Retorna o backend de cache ativo e o prefixo de chaves configurado.",
            responses={**AUTH_ERRORS},
        )
        async def stats() -> dict[str, str]:
            backend = FastAPICache.get_backend()
            return {"backend": type(backend).__name__, "prefix": FastAPICache.get_prefix()}

        @router.post(
            "/clear",
            summary="Limpa todo o cache",
            description="Remove todas as entradas de cache (`energyhub:*`). Ação operacional.",
            responses={**AUTH_ERRORS},
        )
        async def clear() -> dict[str, str]:
            await invalidate_all_cache()
            return {"message": "Cache limpo com sucesso"}
