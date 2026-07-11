## ADDED Requirements

### Requirement: FastAPI Prometheus instrumentation

The system SHALL instrument the FastAPI application with `prometheus-fastapi-instrumentator` so that default HTTP metrics — request totals, request latency histograms, and in-progress requests — are collected for every templated route.

#### Scenario: Instrumentator attached at startup

- **WHEN** the application starts
- **THEN** the Prometheus instrumentator is attached to the FastAPI `app` and begins collecting request, latency, and in-progress metrics

#### Scenario: Latency and in-progress tracking enabled

- **WHEN** a request is served
- **THEN** its duration is recorded in the request-latency histogram and the in-progress gauge reflects concurrently active requests

### Requirement: Metrics endpoint exposure

The system SHALL expose a `/metrics` endpoint in Prometheus text exposition format, and the `/metrics` handler MUST be excluded from its own instrumentation so scraping does not inflate application metrics.

#### Scenario: Metrics endpoint returns Prometheus format

- **WHEN** a client requests `GET /metrics`
- **THEN** the response is HTTP 200 in Prometheus text exposition format containing the collected metric families

#### Scenario: Metrics endpoint excluded from instrumentation

- **WHEN** the `/metrics` endpoint is scraped repeatedly
- **THEN** no request/latency metrics are recorded for the `/metrics` handler itself

### Requirement: Application information metric

The system SHALL publish an `application_info` metric carrying the application name, environment, and version sourced from `settings`.

#### Scenario: Application info reflects settings

- **WHEN** the metrics are scraped
- **THEN** the `application_info` metric reports the application name, the `settings.environment` value, and the current version
