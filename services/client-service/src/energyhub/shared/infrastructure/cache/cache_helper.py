"""Helpers de invalidação de cache (Fase 9).

`invalidate_cache(namespace, key=None)` remove uma chave específica ou o namespace inteiro;
`invalidate_all_cache()` limpa todas as chaves do EnergyHub no backend. Chamados após escritas
(`create`/`update`/`delete`) para que leituras cacheadas nunca contradigam o banco.
"""

from __future__ import annotations

from typing import Any

from fastapi_cache import FastAPICache


async def invalidate_cache(namespace: str, key: str | None = None) -> None:
    """Evicta uma chave (`{prefixo}:{namespace}:{key}`) ou todo o namespace (`key=None`)."""
    if key is None:
        await FastAPICache.clear(namespace=namespace)
    else:
        prefix = FastAPICache.get_prefix()
        await FastAPICache.clear(key=f"{prefix}:{namespace}:{key}")


async def invalidate_all_cache() -> None:
    """Remove **todas** as chaves do keyspace `energyhub:*` no backend."""
    backend: Any = FastAPICache.get_backend()
    redis = backend.redis
    prefix = FastAPICache.get_prefix()
    keys = await redis.keys(f"{prefix}:*")
    if keys:
        await redis.delete(*keys)
