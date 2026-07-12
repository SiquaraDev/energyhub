# data-persistence-volumes Specification

## Purpose
TBD - created by archiving change implement-fase-14. Update Purpose after archive.
## Requirements
### Requirement: Named volumes for stateful services

The system SHALL declare named Docker volumes for every stateful service — PostgreSQL, Redis, RabbitMQ, Elasticsearch, Prometheus, and Grafana — and mount each volume at the service's data directory.

#### Scenario: Volumes are created and mounted

- **WHEN** the stack is started
- **THEN** a named volume exists for each stateful service and is mounted at that service's data path (e.g. `/var/lib/postgresql/data` for PostgreSQL)

### Requirement: Data survives container recreation

Data written to a stateful service SHALL persist across a full `docker-compose down` followed by `docker-compose up -d`, because it is stored on named volumes rather than the container's writable layer.

#### Scenario: Database data persists across a restart cycle

- **WHEN** rows are written to PostgreSQL, then the stack is brought down with `docker-compose down` and back up with `docker-compose up -d`
- **THEN** the previously written rows are still present after restart

#### Scenario: Cache persistence is enabled for Redis

- **WHEN** Redis is configured with append-only persistence and the stack is restarted
- **THEN** keys written before the restart remain available afterward

