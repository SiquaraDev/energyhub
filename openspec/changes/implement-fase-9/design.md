## Context

Fase 6–8 produced use cases, services, and a documented HTTP API on top of the Fase 5 persistence layer. Every read currently reaches PostgreSQL, including reference data (roles, permissions) and slowly changing records (clients, contracts) that are read far more often than written. This phase introduces a Redis-backed read cache to serve repeat reads from memory, reducing database load and tail latency.

The stack additions are fixed by the plan: Redis 7 (`redis:7-alpine`), `redis-py` (async client via `redis.asyncio`), and `fastapi-cache2` with its Redis backend. Configuration is single-sourced through `energyhub.config.settings`, consistent with earlier phases. Authorization reuses the existing `require_permission` dependency and `BaseRouter`. The cache is an accelerator layered onto services that already work without it — correctness must not depend on cache availability.

This phase is additive: it adds a Redis container, cache wiring, decorators, invalidation calls, and an admin router. It does not change the domain model, the schema, or existing endpoint contracts.

## Goals / Non-Goals

**Goals:**
- Run Redis as a Docker service with persistence and a health check, configured entirely from `settings`.
- Initialize a `FastAPICache` Redis backend at application startup with a global `energyhub` prefix and a deterministic key builder.
- Cache read-heavy service methods with per-domain namespaces and explicit TTLs sourced from shared constants.
- Invalidate affected cache entries on every write path so cached reads stay consistent with the database.
- Provide a permission-gated cache admin router for stats introspection and manual clear-all.

**Non-Goals:**
- No new business logic, entities, or query capabilities beyond caching existing reads.
- No caching of write responses, no write-through/write-behind strategies — reads only, with explicit eviction on writes.
- No distributed cache stampede protection, sharding, or Redis clustering (single instance is sufficient at current volume).
- No cache warming/pre-population and no application-level metrics pipeline beyond the `/stats` endpoint.
- No schema, dependency-injection, or authorization framework changes beyond adding the `CACHE_MANAGE` permission.

## Decisions

**Use `fastapi-cache2` with a Redis backend rather than a hand-rolled cache layer:**
- **Decision:** Initialize `FastAPICache` with `RedisBackend(aioredis.from_url(settings.redis_url))` and an `energyhub` prefix, and cache methods with the library's `@cache` decorator.
- **Rationale:** The plan specifies this library; it provides decorator-based caching, namespaces, TTLs, and key builders out of the box, and integrates with the async FastAPI stack already in use.
- **Alternative considered:** A bespoke decorator over the raw `redis-py` async client — rejected as reinventing serialization, namespacing, and key building with more surface area to test and no added benefit at this stage.

**Cache reads only and evict on writes (explicit invalidation), not write-through:**
- **Decision:** Decorate read methods with `@cache`; on `create`/`update`/`delete`, call `invalidate_cache(namespace, key?)` for the affected entries.
- **Rationale:** Read/evict is the simplest model that keeps the database authoritative; writes are comparatively rare, so eviction cost is low and reasoning about correctness is straightforward.
- **Alternative considered:** Write-through/write-behind caching — rejected as more complex and error-prone (dual-write consistency, partial-failure handling) for a workload that is overwhelmingly read-dominated.

**Per-domain namespaces plus tiered TTLs centralized in `CacheConstants`:**
- **Decision:** Give each domain a namespace (`roles`, `permissions`, `clients`, `contracts`, `users`) and choose from `SHORT_TTL`/`DEFAULT_TTL`/`LONG_TTL` based on data volatility; keep all of these in `shared/constant/cache_constants.py`.
- **Rationale:** Namespaces make targeted invalidation possible (clear one domain without touching others); centralized constants prevent drift between the decorator TTL and the invalidation namespace strings.
- **Alternative considered:** A single global TTL and ad-hoc string namespaces at each call site — rejected because it makes invalidation fragile (typos silently miss) and can't match TTL to volatility.

**Deterministic key builder with sorted kwargs:**
- **Decision:** `get_cache_key(prefix, *args, **kwargs)` joins the prefix, stringified positional args, and `sorted(kwargs.items())` with `:` separators; per-method `key_builder` lambdas produce stable keys (e.g. `roles:all`, `clients:{id}`).
- **Rationale:** Stable keys are required for cache hits and for computing the exact keys to invalidate; sorting kwargs removes call-order sensitivity.
- **Alternative considered:** Rely on the library's default argument-hash key builder — rejected because opaque hashed keys are hard to target for precise invalidation.

**Cache admin router is permission-gated behind `CACHE_MANAGE`:**
- **Decision:** Mount `CacheRouter` at `/api/v1/cache` with `Depends(require_permission("CACHE_MANAGE"))`; expose `GET /stats` and `POST /clear`.
- **Rationale:** Clearing the cache is an operational action with performance impact (a stampede of cold reads); it must be restricted to authorized operators. Reuses the existing authorization primitives.
- **Alternative considered:** Leaving admin endpoints unauthenticated for convenience — rejected as an operational and security risk.

## Risks / Trade-offs

- **Stale reads within a TTL window** → Choose TTLs by volatility (short for mutable data, long for reference data) and evict on writes; residual staleness is bounded by the TTL and is acceptable for the affected read paths.
- **Missed invalidation leaves stale entries** → Centralize namespaces/keys in `CacheConstants` and keep key builders and invalidation keys symmetric; cover create/update/delete eviction with tests so a missing eviction is caught early.
- **Redis unavailability degrades cached paths** → Treat the cache as best-effort: services remain correct without it, and cache errors should fall back to the database rather than failing the request; the `redis-cli ping` health check surfaces outages.
- **Cache-clear stampede** → A manual `POST /clear` forces every cached read cold at once; gate it behind `CACHE_MANAGE` and document it as an operational action, not a routine one.
- **Key collisions from a weak key builder** → Deterministic, sorted-kwarg keys under a global prefix and per-domain namespaces keep keys unique and predictable.
- **Extra runtime dependency** → Redis is now required for cached paths; running it in `docker-compose.yml` alongside PostgreSQL keeps local and CI environments consistent.

## Migration Plan

1. Add the `redis` service and `redis_data` volume to `docker-compose.yml`; bring it up and confirm `redis-cli ping` returns `PONG`.
2. Add the `redis` and `fastapi-cache2[redis]` dependencies and the Redis settings in `energyhub/config.py`.
3. Add `CacheConfig` (backend init + key builder) and call `init_cache()` on application startup; confirm the app starts with no Redis connection errors.
4. Add `CacheConstants` and decorate read methods on services with `@cache`; verify cache hits on repeat reads.
5. Add the invalidation helpers and wire eviction into `create`/`update`/`delete`; verify writes evict the expected entries.
6. Add the `CACHE_MANAGE` permission and the `CacheRouter`; verify `/stats` and `/clear` behind authorization.
7. Rollback: this phase is additive; reverting the branch removes cache wiring, and stopping the Redis container returns the system to direct database reads with no data loss.

## Open Questions

- Should cache errors fail open (fall back to the database, log, and continue) globally, or should some critical paths surface the error? (Current lean: fail open for reads; confirm per endpoint when wiring.)
- Exact TTL values per domain — the plan suggests `SHORT_TTL=300`, `DEFAULT_TTL=600`, `LONG_TTL=3600`; final tiers per namespace to be tuned against observed volatility.
- Where should the `CACHE_MANAGE` permission be seeded (Fase 4 seed data vs. this phase), and which roles receive it by default?
- Is a manual `POST /clear` sufficient, or is namespace-scoped clearing needed from the admin router for finer operational control? (Deferred until an operational need appears.)
