"""Configuração do backend de cache (fastapi-cache2 + Redis) — Fase 9.

`CacheConfig.init_cache()` inicializa o `FastAPICache` com um `RedisBackend` ligado a
`settings.redis_url` e o prefixo global `energyhub`, usando o `PickleCoder` (round-trip fiel de
DTOs Pydantic). Os *key builders* produzem chaves estáveis e ignoram o `self` do método de serviço.
"""

from __future__ import annotations

from typing import Any

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.coder import PickleCoder
from redis import asyncio as aioredis

from energyhub.config.settings import settings
from energyhub.shared.constant.cache_constants import CACHE_KEY_PREFIX


class CacheConfig:
    """Inicialização do cache e construção determinística de chaves."""

    @staticmethod
    def init_cache() -> None:
        """Configura o `FastAPICache` (RedisBackend + prefixo `energyhub` + PickleCoder)."""
        redis = aioredis.from_url(settings.redis_url)
        FastAPICache.init(RedisBackend(redis), prefix=CACHE_KEY_PREFIX, coder=PickleCoder)

    @staticmethod
    def get_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
        """Junta prefixo + args posicionais + kwargs **ordenados** numa chave determinística."""
        parts = [str(prefix), *(str(a) for a in args)]
        parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return ":".join(parts)


# --- Key builders para o decorador `@cache` (fastapi-cache2) ---
# fastapi-cache2 chama: key_builder(func, namespace, *, request, response, args, kwargs), onde
# `namespace` JÁ vem prefixado (ex.: "energyhub:roles") e `args[0]` é o `self` do serviço.


def id_key_builder(
    func: Any,
    namespace: str = "",
    *,
    request: Any = None,
    response: Any = None,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> str:
    """Chave por identificador simples: `find_by_id(id)`, `find_by_name(name)`, etc."""
    kwargs = kwargs or {}
    ident = args[1] if len(args) > 1 else next(iter(kwargs.values()), "")
    return CacheConfig.get_cache_key(namespace, ident)


def page_key_builder(
    func: Any,
    namespace: str = "",
    *,
    request: Any = None,
    response: Any = None,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> str:
    """Chave por parâmetros de paginação: `find_all(page_request)`."""
    kwargs = kwargs or {}
    page_request = args[1] if len(args) > 1 else kwargs.get("page_request")
    if page_request is not None:
        return CacheConfig.get_cache_key(
            namespace,
            "all",
            page_request.page,
            page_request.size,
            page_request.sort,
            page_request.direction,
        )
    return CacheConfig.get_cache_key(namespace, "all")
