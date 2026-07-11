## ADDED Requirements

### Requirement: Grafana server

The system SHALL run a Grafana server as a Docker Compose service with a persistent data volume and admin credentials supplied via environment variables, depending on the Prometheus service.

#### Scenario: Grafana service defined

- **WHEN** the observability stack is started via `docker-compose up -d grafana`
- **THEN** a Grafana container runs, persists its data to a named volume, and starts after Prometheus

### Requirement: Prometheus data source

The system SHALL configure Prometheus as a Grafana data source pointing at the Prometheus service so dashboards can query metrics.

#### Scenario: Data source connects to Prometheus

- **WHEN** the Prometheus data source is saved and tested in Grafana
- **THEN** the connection to `http://prometheus:9090` succeeds and the data source is available to dashboards

### Requirement: Observability dashboards

The system SHALL provide application, business, and infrastructure dashboards that visualize the collected metrics.

#### Scenario: Application dashboard panels

- **WHEN** the application dashboard is opened
- **THEN** it displays request throughput, latency percentiles (p50/p95/p99), error rate, and Python resource usage panels

#### Scenario: Business dashboard panels

- **WHEN** the business dashboard is opened
- **THEN** it displays business KPIs such as active clients, contracts by status, and invoices issued versus paid

#### Scenario: Infrastructure dashboard panels

- **WHEN** the infrastructure dashboard is opened
- **THEN** it displays host resource usage and dependency health such as cache hit rate and Elasticsearch latency
