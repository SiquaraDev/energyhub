## ADDED Requirements

### Requirement: Cache administration router

The system SHALL provide a `CacheRouter` (extending the shared `BaseRouter`) mounted at `/api/v1/cache` that exposes cache monitoring and management endpoints.

#### Scenario: Router is registered under the cache prefix

- **WHEN** the application includes the cache router
- **THEN** the cache endpoints are reachable under the `/api/v1/cache` prefix and grouped under the `Cache` tag

### Requirement: Cache statistics endpoint

The cache router SHALL expose `GET /stats` returning backend introspection details (such as the backend identity and active key prefix) for monitoring.

#### Scenario: Stats returns backend information

- **WHEN** a client sends `GET /api/v1/cache/stats`
- **THEN** the response reports the active cache backend and its configured prefix

### Requirement: Manual cache clear endpoint

The cache router SHALL expose `POST /clear` that clears all cache entries and confirms the operation.

#### Scenario: Clear removes all cached entries

- **WHEN** a client sends `POST /api/v1/cache/clear`
- **THEN** all cache entries are cleared and the response confirms the caches were cleared

### Requirement: Cache management is permission-gated

Cache administration endpoints SHALL require the `CACHE_MANAGE` permission so only authorized operators can inspect or clear the cache.

#### Scenario: Authorized operator manages the cache

- **WHEN** a request to a cache administration endpoint carries the `CACHE_MANAGE` permission
- **THEN** the request is allowed to proceed

#### Scenario: Unauthorized request is rejected

- **WHEN** a request to a cache administration endpoint lacks the `CACHE_MANAGE` permission
- **THEN** the request is denied with an authorization error and no cache operation is performed
