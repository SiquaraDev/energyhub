# environment-validation Specification

## Purpose
TBD - created by archiving change implement-fase-14. Update Purpose after archive.
## Requirements
### Requirement: Full stack boots healthy

The system SHALL support bringing the entire stack up with a single command and confirming that every service reaches a healthy or running state.

#### Scenario: All services report healthy after startup

- **WHEN** `docker-compose up -d` is run and the stack is given time to initialize
- **THEN** `docker-compose ps` shows every service running, and health-checked services (PostgreSQL, RabbitMQ, Elasticsearch, Redis) report healthy

### Requirement: API health endpoint responds in the container

The containerized API SHALL expose a health endpoint that confirms the application is serving inside the stack.

#### Scenario: Health check returns success

- **WHEN** `GET /health` is requested against the running API container
- **THEN** the endpoint responds successfully

### Requirement: End-to-end integration smoke test

The system SHALL be validated by an end-to-end smoke test exercising the core cross-service flow: create a user, create a client, create a contract, and confirm cache, messaging, and search participation.

#### Scenario: Core flow succeeds across services

- **WHEN** the smoke test runs against the started stack
- **THEN** the user, client, and contract are created successfully and the cache, messaging, and search integrations respond as expected

### Requirement: Data persists across a shutdown/startup cycle

The system SHALL preserve application data across a full `docker-compose down` and `docker-compose up -d` cycle.

#### Scenario: Data survives a full restart

- **WHEN** data is created, the stack is stopped with `docker-compose down`, and then started again with `docker-compose up -d`
- **THEN** the previously created data is still present and the stack returns to a healthy state

