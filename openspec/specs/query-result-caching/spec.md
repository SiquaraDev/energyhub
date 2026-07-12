# query-result-caching Specification

## Purpose
TBD - created by archiving change implement-fase-9. Update Purpose after archive.
## Requirements
### Requirement: Cached read operations

Read-heavy service query methods (such as `find_all`, `find_by_id`, `find_by_name`, and `find_by_cnpj`) SHALL be decorated with `@cache` using a per-domain namespace and an explicit expiry so repeat reads are served from Redis rather than the database.

#### Scenario: First read populates the cache

- **WHEN** a cached query method is invoked and no matching entry exists
- **THEN** the underlying repository is queried and the mapped result is stored in Redis under the method's namespace and key

#### Scenario: Subsequent read is served from cache

- **WHEN** the same cached query method is invoked again before its TTL expires
- **THEN** the result is returned from Redis without querying the database

#### Scenario: Entry expires after its TTL

- **WHEN** a cached entry's configured expiry elapses
- **THEN** the next invocation re-queries the database and repopulates the cache

### Requirement: Centralized cache constants

The system SHALL define a `CacheConstants` class in `shared/constant/cache_constants.py` declaring the domain namespaces (e.g. `ROLES`, `PERMISSIONS`, `CLIENTS`, `CONTRACTS`, `USERS`) and reusable TTL values (`DEFAULT_TTL`, `SHORT_TTL`, `LONG_TTL`).

#### Scenario: Services reference shared namespaces and TTLs

- **WHEN** a service applies a cache decorator or invalidates a namespace
- **THEN** it uses a namespace and TTL sourced from `CacheConstants` rather than a hard-coded literal

#### Scenario: TTL tiers are distinct

- **WHEN** the TTL constants are read
- **THEN** `SHORT_TTL`, `DEFAULT_TTL`, and `LONG_TTL` provide distinct, increasing expiry durations for different data-volatility tiers

