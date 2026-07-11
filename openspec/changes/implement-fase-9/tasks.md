## 1. Redis Cache Infrastructure

- [ ] 1.1 Add a `redis` service to `docker-compose.yml` (`redis:7-alpine`, `--appendonly yes`, published port `6379`, named `redis_data` volume)
- [ ] 1.2 Add a `redis-cli ping` health check to the `redis` service with interval/timeout/retries
- [ ] 1.3 Bring up the container (`docker-compose up -d redis`) and confirm `docker exec ... redis-cli ping` returns `PONG`
- [ ] 1.4 Add `redis` and `fastapi-cache2[redis]` to `pyproject.toml` and install (`poetry add redis fastapi-cache2[redis]`)
- [ ] 1.5 Add Redis settings to `energyhub/config.py` (`redis_host`, `redis_port`, `redis_db`, `redis_password`, derived `redis_url`) with env-var overrides

## 2. Cache Backend Configuration

- [ ] 2.1 Create `shared/infrastructure/cache/cache_config.py` with a `CacheConfig` class
- [ ] 2.2 Implement `CacheConfig.init_cache()` initializing `FastAPICache` with `RedisBackend(aioredis.from_url(settings.redis_url))` and the `energyhub` prefix
- [ ] 2.3 Implement `CacheConfig.get_cache_key(prefix, *args, **kwargs)` joining prefix, args, and sorted kwargs into a deterministic key
- [ ] 2.4 Call `CacheConfig.init_cache()` from the application startup lifecycle in `energyhub/main.py`
- [ ] 2.5 Start the app (`poetry run uvicorn energyhub.main:app --reload`) and confirm no Redis connection errors at startup

## 3. Cache Constants

- [ ] 3.1 Create `shared/constant/cache_constants.py` with a `CacheConstants` class
- [ ] 3.2 Declare domain namespaces (`ROLES`, `PERMISSIONS`, `CLIENTS`, `CONTRACTS`, `USERS`)
- [ ] 3.3 Declare TTL tiers (`SHORT_TTL`, `DEFAULT_TTL`, `LONG_TTL`) with distinct, increasing durations

## 4. Query Result Caching

- [ ] 4.1 Decorate `RoleService` read methods (`find_all`, `find_by_name`) with `@cache` using the `roles` namespace, an explicit TTL, and stable key builders
- [ ] 4.2 Decorate `PermissionService` read methods (`find_all`, `find_by_role_name`) with `@cache` using the `permissions` namespace
- [ ] 4.3 Decorate `ClientService` read methods (`find_by_id`, `find_by_cnpj`) with `@cache` using the `clients` namespace and a short TTL
- [ ] 4.4 Extend caching to the remaining read-heavy services (e.g. contracts, users) using namespaces and TTLs from `CacheConstants`
- [ ] 4.5 Verify repeat reads are served from Redis (cache hit) and that entries repopulate after TTL expiry

## 5. Cache Invalidation

- [ ] 5.1 Create `shared/infrastructure/cache/cache_helper.py` with `invalidate_cache(namespace, key=None)` (clears a key or a whole namespace)
- [ ] 5.2 Add `invalidate_all_cache()` clearing the entire cache backend
- [ ] 5.3 Invalidate affected list/collection entries in service `create` methods
- [ ] 5.4 Invalidate entity-keyed entries (e.g. id and cnpj) in service `update` methods
- [ ] 5.5 Invalidate entity-keyed entries in service `delete` methods
- [ ] 5.6 Verify a write is immediately reflected on the next read (no stale cached value)

## 6. Cache Administration

- [ ] 6.1 Add the `CACHE_MANAGE` permission (constant and seed) used to gate cache endpoints
- [ ] 6.2 Create `shared/presentation/router/cache_router.py` with a `CacheRouter(BaseRouter)` and route setup
- [ ] 6.3 Implement `GET /stats` returning backend identity and active prefix
- [ ] 6.4 Implement `POST /clear` calling `invalidate_all_cache()` and returning a confirmation
- [ ] 6.5 Mount the router at `/api/v1/cache` with the `Cache` tag and `Depends(require_permission("CACHE_MANAGE"))`

## 7. Validation

- [ ] 7.1 Confirm cached endpoints return correct data on hit, miss, and after invalidation
- [ ] 7.2 Verify `GET /api/v1/cache/stats` and `POST /api/v1/cache/clear` behave correctly and enforce `CACHE_MANAGE`
- [ ] 7.3 Measure that a repeat cached read avoids the database and improves response latency
- [ ] 7.4 Run `openspec validate implement-fase-9` and confirm the change is valid
