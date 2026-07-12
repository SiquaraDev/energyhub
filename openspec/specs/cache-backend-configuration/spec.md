# cache-backend-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-9. Update Purpose after archive.
## Requirements
### Requirement: Cache backend initialization

The system SHALL provide a `CacheConfig` in `shared/infrastructure/cache/` that initializes `FastAPICache` with a `RedisBackend` connected to `settings.redis_url` and a global `energyhub` key prefix.

#### Scenario: Cache initialized on application startup

- **WHEN** the application startup lifecycle runs `CacheConfig.init_cache()`
- **THEN** `FastAPICache` is configured with a `RedisBackend` bound to `settings.redis_url` and the `energyhub` prefix, ready to serve cached responses

#### Scenario: Cached keys are namespaced by prefix

- **WHEN** a value is cached through the configured backend
- **THEN** the stored Redis key is prefixed with `energyhub` so cache entries are isolated from other keyspaces

### Requirement: Deterministic cache-key builder

`CacheConfig` SHALL provide a `get_cache_key(prefix, *args, **kwargs)` helper that produces a stable, collision-resistant key by joining the prefix, positional arguments, and sorted keyword arguments.

#### Scenario: Same inputs produce the same key

- **WHEN** `get_cache_key` is called twice with identical prefix, args, and kwargs
- **THEN** it returns an identical key string on both calls

#### Scenario: Keyword argument order does not change the key

- **WHEN** `get_cache_key` is called with the same keyword arguments supplied in a different order
- **THEN** it returns the same key because keyword arguments are sorted before joining

