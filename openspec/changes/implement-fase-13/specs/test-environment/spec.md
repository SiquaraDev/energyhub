## ADDED Requirements

### Requirement: Test infrastructure compose file

The project SHALL provide a `docker-compose.test.yml` that defines isolated PostgreSQL, Redis, and RabbitMQ services for testing, bound to non-default host ports so they do not collide with local development services.

#### Scenario: Test infrastructure starts in isolation

- **WHEN** `docker-compose -f docker-compose.test.yml up -d` is run
- **THEN** dedicated test PostgreSQL, Redis, and RabbitMQ containers start on the configured non-default ports (e.g. 5433, 6380, 5673) without interfering with development containers

### Requirement: Session-scoped test environment configuration

The suite SHALL set the environment variables the application reads (`DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`) to point at the test infrastructure, applied once per test session before the application configuration is loaded.

#### Scenario: Application targets the test infrastructure during a run

- **WHEN** the test session starts
- **THEN** a session-scoped, autouse fixture sets `DATABASE_URL`, `REDIS_URL`, and `RABBITMQ_URL` to the test endpoints so the application under test connects to the test infrastructure and never to a development or production instance

#### Scenario: Configuration does not leak beyond the session

- **WHEN** the test session ends
- **THEN** the test environment configuration applies only to the test process and leaves the developer's shell environment unchanged
