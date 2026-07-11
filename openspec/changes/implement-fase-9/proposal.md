## Why

Fase 6–8 delivered use cases, services, and a documented HTTP API, but every read hits PostgreSQL on each request — including reference data (roles, permissions) and slowly changing records (clients, contracts) that rarely mutate between reads. This phase adds a Redis-backed cache so repeat reads are served from memory, cutting database load and response latency, while explicit write-time invalidation keeps cached responses correct.

## What Changes

- Add a `redis` service to `docker-compose.yml` (image `redis:7-alpine`, `--appendonly yes`, a named `redis_data` volume, and a `redis-cli ping` healthcheck) so a cache backend runs alongside PostgreSQL.
- Add the `redis` and `fastapi-cache2[redis]` dependencies and Redis connection settings (`redis_host`, `redis_port`, `redis_db`, `redis_password`, `redis_url`) to `energyhub/config.py`.
- Add a `CacheConfig` in `shared/infrastructure/cache/` that initializes `FastAPICache` with a `RedisBackend` and an `energyhub` prefix on application startup, plus a deterministic `get_cache_key(...)` builder.
- Cache read-heavy service methods (`find_all`, `find_by_id`, `find_by_name`, `find_by_cnpj`, …) with the `@cache` decorator using per-domain namespaces and TTLs, and centralize namespaces/TTLs in `shared/constant/cache_constants.py`.
- Add cache-invalidation helpers (`invalidate_cache(namespace, key?)`, `invalidate_all_cache()`) and call them after write operations (`create`/`update`/`delete`) so stale entries are evicted.
- Add a permission-gated `CacheRouter` exposing cache stats (`GET /stats`) and a manual clear-all endpoint (`POST /clear`) for monitoring and operations.

## Capabilities

### New Capabilities

- `redis-cache-infrastructure`: A Redis container in `docker-compose.yml` (healthcheck + persistence) and typed Redis connection settings in application configuration, providing the cache backing store.
- `cache-backend-configuration`: A `CacheConfig` that initializes `FastAPICache` with a `RedisBackend`, a global key prefix, and a deterministic cache-key builder, wired into the app startup lifecycle.
- `query-result-caching`: `@cache`-decorated read methods on services with per-domain namespaces and TTLs, plus centralized `CacheConstants` (namespaces and default/short/long TTLs).
- `cache-invalidation`: Helper functions to evict entries by namespace/key or clear everything, invoked after create/update/delete so cached reads stay consistent with the database.
- `cache-administration`: A permission-gated cache router exposing backend/stats introspection and a manual clear-all operation for monitoring and incident response.

### Modified Capabilities

None — `openspec/specs/` contains no materialized capabilities yet; every capability in this phase is new. The cache decorators and invalidation calls attach to Fase 6–8 services, but they introduce new caching behavior rather than changing previously specified requirements.

## Impact

- **Dependencies**: Adds `redis` (`^5.0.0`) and `fastapi-cache2[redis]` (`^0.2.0`) to `pyproject.toml`. Adds a running Redis instance as a runtime dependency for cached paths.
- **Consumes**: Read/write services from Fase 6–8, the `energyhub.config.settings` configuration, the `BaseRouter` and `require_permission` authorization from earlier phases, and the existing `docker-compose.yml`.
- **Provides**: `CacheConfig` and `get_cache_key`, `CacheConstants`, the `invalidate_cache`/`invalidate_all_cache` helpers, and the `CacheRouter` mounted at `/api/v1/cache` — reusable caching primitives for current and future modules.
- **New artifacts**: `shared/infrastructure/cache/` (config + invalidation helpers), `shared/constant/cache_constants.py`, `shared/presentation/router/cache_router.py`, a `redis` service and `redis_data` volume in `docker-compose.yml`, and cache/invalidation edits on existing services.
- **Coordination**: Requires a new `CACHE_MANAGE` permission for the cache router; the cache is a best-effort accelerator — correctness must never depend on it, so invalidation is treated as mandatory on every write path that has a cached read.
