# elasticsearch-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-11. Update Purpose after archive.
## Requirements
### Requirement: Dockerized Elasticsearch service

The system SHALL run Elasticsearch as a Docker Compose service configured for single-node local development, with security disabled, a bounded JVM heap, a persistent data volume, and a cluster-health healthcheck.

#### Scenario: Elasticsearch service starts and reports healthy

- **WHEN** `docker-compose up -d elasticsearch` is run
- **THEN** the `elasticsearch` container starts, exposes port `9200`, and its healthcheck against `_cluster/health` eventually reports the service as healthy

#### Scenario: Index data survives container restart

- **WHEN** the Elasticsearch container is restarted
- **THEN** previously created indices and documents remain available because the data directory is backed by a persistent volume

### Requirement: Elasticsearch application settings

The system SHALL expose Elasticsearch connection settings (`elasticsearch_url` and `elasticsearch_timeout`) through `energyhub.config.settings`, single-sourced with the rest of the application configuration.

#### Scenario: Client reads connection settings from config

- **WHEN** an Elasticsearch client is constructed
- **THEN** it uses `settings.elasticsearch_url` as its host and `settings.elasticsearch_timeout` as its request timeout

### Requirement: Elasticsearch client factory and index bootstrap

The system SHALL provide a shared `ElasticsearchConfig` in `shared/infrastructure/search/` that exposes a `get_client()` factory returning a configured `Elasticsearch` client and a `create_indices()` operation that creates each configured index only when it does not already exist.

#### Scenario: Client factory returns a configured client

- **WHEN** `ElasticsearchConfig.get_client()` is called
- **THEN** it returns an `Elasticsearch` client bound to the configured URL and timeout

#### Scenario: Index creation is idempotent

- **WHEN** `create_indices()` is called and an index already exists
- **THEN** the existing index is left unchanged and only missing indices are initialized, so repeated calls do not error

