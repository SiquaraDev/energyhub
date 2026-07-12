# prometheus-scraping Specification

## Purpose
TBD - created by archiving change implement-fase-12. Update Purpose after archive.
## Requirements
### Requirement: Prometheus server

The system SHALL run a Prometheus server as a Docker Compose service with a persistent data volume and a mounted configuration file, so metrics are collected and retained across restarts.

#### Scenario: Prometheus service defined

- **WHEN** the observability stack is started via `docker-compose up -d prometheus`
- **THEN** a Prometheus container runs, mounts `prometheus/prometheus.yml`, and persists its time-series data to a named volume

### Requirement: Application scrape configuration

The Prometheus configuration SHALL define a scrape job targeting the application's `/metrics` endpoint on a defined scrape interval.

#### Scenario: Application target scraped

- **WHEN** Prometheus reloads its configuration
- **THEN** it scrapes the `energyhub` job at the application's `/metrics` path on the configured interval

#### Scenario: Target reported healthy

- **WHEN** the application is running and reachable
- **THEN** the `energyhub` target is reported UP on the Prometheus targets page

### Requirement: Collected metrics are queryable

The system SHALL make the application, business, and resource metrics queryable through Prometheus once scraping is active.

#### Scenario: Custom metric returned by query

- **WHEN** a PromQL query such as `client_created_total` or `rate(fastapi_request_duration_seconds_count[5m])` is executed
- **THEN** Prometheus returns the corresponding scraped series

