# container-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-14. Update Purpose after archive.
## Requirements
### Requirement: Environment-variable-driven configuration

The application container SHALL receive all runtime configuration through environment variables — including `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `SECRET_KEY`, and `ENVIRONMENT` — and SHALL contain no hard-coded connection strings or secrets baked into the image.

#### Scenario: Configuration is injected at run time

- **WHEN** the API container starts with the configured environment variables set by Compose
- **THEN** the application reads its database, cache, messaging, search, secret, and environment settings from those variables

#### Scenario: The same image runs in a different environment

- **WHEN** the identical image is started with a different set of environment-variable values
- **THEN** the application connects to the new targets without rebuilding the image

### Requirement: Service endpoints reference in-network hostnames

The injected connection URLs SHALL address dependencies by their Compose service names (e.g. `postgres`, `redis`, `rabbitmq`, `elasticsearch`) rather than `localhost`.

#### Scenario: Connection URLs use service names

- **WHEN** `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, and `ELASTICSEARCH_URL` are supplied to the API service
- **THEN** each URL targets the dependency by its service hostname on the shared network

### Requirement: Service credentials provided via configuration

The stateful services SHALL receive their initial users and passwords through environment variables (e.g. `POSTGRES_USER`/`POSTGRES_PASSWORD`, `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS`), and these defaults SHALL be documented as development placeholders to be rotated before production.

#### Scenario: Stateful services initialize with configured credentials

- **WHEN** PostgreSQL and RabbitMQ containers start
- **THEN** they create the users and passwords supplied via their environment variables

