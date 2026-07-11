## ADDED Requirements

### Requirement: Containerized Prometheus with mounted config

The system SHALL define a Prometheus service that mounts a `prometheus/prometheus.yml` scrape configuration from the project and persists its time-series data on a named volume.

#### Scenario: Prometheus starts with the provided config

- **WHEN** the Prometheus container starts
- **THEN** it loads the mounted `prometheus.yml` scrape configuration and is reachable on port `9090`

### Requirement: Containerized Grafana ordered after Prometheus

The system SHALL define a Grafana service that depends on Prometheus, exposes port `3000`, initializes its admin credentials via environment variables, and persists its state on a named volume.

#### Scenario: Grafana starts after Prometheus

- **WHEN** the observability services are started
- **THEN** Prometheus starts first and Grafana starts afterward, reachable on port `3000` with the configured admin credentials

#### Scenario: Grafana state persists across restarts

- **WHEN** Grafana configuration is stored and the stack is restarted
- **THEN** the stored Grafana state remains available because it is kept on a named volume
