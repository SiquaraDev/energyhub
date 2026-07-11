## ADDED Requirements

### Requirement: Redis cache service

The system SHALL define a `redis` service in `docker-compose.yml` using the `redis:7-alpine` image with append-only persistence (`--appendonly yes`), a named `redis_data` volume, and the port published for local development.

#### Scenario: Redis container starts and accepts connections

- **WHEN** `docker-compose up -d redis` is run
- **THEN** the `redis` container starts and responds to `redis-cli ping` with `PONG`

#### Scenario: Cached data survives a restart

- **WHEN** the Redis container is restarted with the `redis_data` volume attached
- **THEN** append-only persisted keys remain available after the restart

### Requirement: Redis service health check

The Redis service SHALL declare a health check that runs `redis-cli ping` on an interval so orchestration can determine readiness before dependent services rely on the cache.

#### Scenario: Health check reports readiness

- **WHEN** the Redis service is queried for health status after startup
- **THEN** the health check reports the service as healthy once `redis-cli ping` succeeds

### Requirement: Redis connection settings

The system SHALL expose typed Redis connection settings in `energyhub/config.py` (`redis_host`, `redis_port`, `redis_db`, optional `redis_password`, and a derived `redis_url`), overridable via environment variables, so cache wiring reads all connection detail from `settings`.

#### Scenario: Connection URL derived from settings

- **WHEN** the application reads `settings.redis_url`
- **THEN** it returns a `redis://host:port/db` URL built from the configured host, port, and database values

#### Scenario: Settings overridden by environment

- **WHEN** `redis_host` or `redis_port` is provided via environment variables
- **THEN** the corresponding setting reflects the environment value instead of the default
