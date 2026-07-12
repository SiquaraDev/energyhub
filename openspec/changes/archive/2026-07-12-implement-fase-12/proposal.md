## Why

Earlier phases built the application, its persistence, messaging, and centralized logging (Fase 11), but the platform is still opaque at runtime: there is no way to see request throughput, latency, error rates, business volumes, or host resource pressure, and nothing fires when the system degrades. This phase adds real-time observability — Prometheus metrics, Grafana dashboards, and alerting — so operators can watch behavior live and be notified before incidents become outages.

## What Changes

- Instrument the FastAPI application with `prometheus-fastapi-instrumentator`, exposing a `/metrics` endpoint and default HTTP metrics (request count, latency histograms, in-progress requests), with `/metrics` excluded from its own instrumentation and an `application_info` metric describing environment and version.
- Add a `MetricsConfig` factory in `shared/infrastructure/metrics/` that centralizes custom Prometheus collectors (counters, gauges, histograms) and a `BusinessMetrics` helper, then instrument services to record business events (clients created, contracts created by status, invoices paid, active clients) and per-operation duration.
- Add system-resource metrics (memory, CPU, disk) collected via `psutil` and exposed as Prometheus gauges refreshed on scrape.
- Add a Prometheus server to `docker-compose.yml` with a `prometheus.yml` scrape configuration targeting the application `/metrics`, plus a persistent data volume.
- Add a Grafana server to `docker-compose.yml`, provision the Prometheus data source, and define application, business, and infrastructure dashboards (throughput, latency percentiles, error rate, resource usage, business KPIs), including imported community dashboards.
- Add Prometheus alert rules (`alerts.yml`) and an Alertmanager service (`alertmanager.yml`) with notification receivers (email/Slack/webhook) for high latency, high error rate, and low-resource conditions.

## Capabilities

### New Capabilities

- `metrics-instrumentation`: FastAPI instrumented with Prometheus, exposing `/metrics` with default HTTP request/latency/in-progress metrics and an application-info metric, `/metrics` excluded from instrumentation.
- `custom-application-metrics`: A `MetricsConfig` factory and `BusinessMetrics` helper defining custom counters/gauges/histograms, with services instrumented to record business events and operation durations.
- `system-resource-metrics`: Host resource gauges (memory, CPU, disk) collected via `psutil` and exposed through Prometheus.
- `prometheus-scraping`: A Prometheus server, scrape configuration, and persistent storage that collect the application's exposed metrics on a defined interval.
- `grafana-dashboards`: A Grafana server with a provisioned Prometheus data source and application/business/infrastructure dashboards for visualization.
- `alerting`: Prometheus alert rules and an Alertmanager with notification receivers that fire on high latency, high error rate, and low-resource conditions.

### Modified Capabilities

None — this phase introduces the observability layer; it does not change previously specified requirements.

## Impact

- **Dependencies**: Adds `prometheus-client`, `prometheus-fastapi-instrumentator`, and `psutil` to `pyproject.toml`. Adds `prom/prometheus`, `grafana/grafana`, and `prom/alertmanager` container images.
- **Prerequisites**: Fase 11 completed (centralized logging), with Elasticsearch and Docker running.
- **Consumes**: `energyhub.config.settings` (environment, version) and the existing FastAPI `app` in `energyhub/main.py`; hooks into services from earlier phases to record business events.
- **Provides**: `energyhub.shared.infrastructure.metrics` (metrics factory + business metrics), the `/metrics` endpoint, and the Prometheus/Grafana/Alertmanager stack that operators use to monitor the platform.
- **New artifacts**: `shared/infrastructure/metrics/` (metrics config, business metrics, system metrics), `prometheus/` (`prometheus.yml`, `alerts.yml`, `alertmanager.yml`), and Grafana provisioning/dashboards, plus new services and volumes in `docker-compose.yml`.
- **Operational**: Exposes new ports (Prometheus `9090`, Grafana `3000`, Alertmanager `9093`); default Grafana and SMTP credentials are placeholders and must be replaced before any non-local use.
