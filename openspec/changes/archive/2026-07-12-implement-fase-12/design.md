## Context

The EnergyHub application, persistence, messaging, and centralized logging (Fase 11) are in place, but there is no runtime visibility: no metrics endpoint, no dashboards, and no alerts. Logs (Fase 11) answer "what happened" after the fact; this phase adds the complementary "what is happening now" via numeric time series.

The stack is a FastAPI app configured through `energyhub.config.settings`, already run under Docker Compose alongside PostgreSQL, the message broker, and Elasticsearch. The observability tooling is fixed by the plan: `prometheus-client` + `prometheus-fastapi-instrumentator` for exposition, Prometheus for collection/storage, Grafana for visualization, and Alertmanager for notification. This is an additive, cross-cutting change — it touches `main.py`, adds a `shared/infrastructure/metrics/` module, instruments existing services, and extends `docker-compose.yml` with three new services — but it introduces no schema or API-contract changes to existing endpoints.

## Goals / Non-Goals

**Goals:**
- Expose a Prometheus `/metrics` endpoint with default HTTP metrics and an application-info metric, with `/metrics` excluded from its own instrumentation.
- Centralize custom collectors in a `MetricsConfig` factory and instrument services to emit business metrics and operation durations.
- Collect host resource metrics (memory, CPU, disk) via `psutil`.
- Run Prometheus, Grafana, and Alertmanager under Docker Compose with scrape config, dashboards, and alert rules.
- Fire alerts on high latency, high error rate, and low resources, routed to a notification receiver.

**Non-Goals:**
- No distributed tracing (OpenTelemetry spans) — metrics and alerting only.
- No changes to application business logic beyond adding metric recording calls.
- No production-grade secrets management for Grafana/SMTP credentials — placeholders are used and flagged for rotation.
- No long-term metrics storage backend (Thanos/Cortex) or high-availability Prometheus.
- No SLO/error-budget modeling — threshold-based alerts only.

## Decisions

**Use `prometheus-fastapi-instrumentator` for default HTTP metrics rather than hand-rolled middleware:**
- **Decision:** Attach the instrumentator to `app` and `expose` it at `/metrics`, configuring it to exclude the `/metrics` handler, group untemplated paths, and track in-progress requests and latency.
- **Rationale:** It provides correct, well-labeled request/latency/in-progress metrics out of the box and matches the plan; hand-written middleware would re-implement the same histograms with more risk of label cardinality mistakes.
- **Alternative considered:** Custom ASGI middleware emitting metrics directly — rejected as more code and a common source of high-cardinality label bugs, with no benefit at this scope.

**Centralize custom collectors in a `MetricsConfig` factory instead of module-level globals scattered across services:**
- **Decision:** Define counters/gauges/histograms behind `MetricsConfig` factory methods in `shared/infrastructure/metrics/`, and have services and a `BusinessMetrics` helper obtain collectors from it.
- **Rationale:** Prometheus collectors must be registered exactly once per name; a single factory prevents duplicate-registration errors, keeps metric names/labels consistent, and gives one place to evolve the metric catalog.
- **Alternative considered:** Declaring collectors as globals in each service module — rejected; it scatters metric definitions, invites duplicate registration under the default registry, and makes label conventions drift.

**Record business metrics inside existing services at the point of the event:**
- **Decision:** Instrument service operations (e.g. client/contract/invoice flows) to increment counters and observe durations at the moment the business event succeeds, initializing labeled series to zero at startup.
- **Rationale:** Co-locating the metric with the event keeps counts accurate and avoids a separate polling path; zero-initialization ensures dashboards render before the first event.
- **Alternative considered:** Deriving business counts by querying the database on a timer — rejected; it adds DB load, lags real time, and double-counts across replicas.

**Collect host resource metrics via `psutil` refreshed on scrape:**
- **Decision:** Expose `memory_usage_bytes`, `cpu_usage_percent`, and `disk_usage_percent` gauges updated from `psutil` at collection time.
- **Rationale:** Simple, dependency-light, and sufficient for single-host visibility per the plan.
- **Alternative considered:** Deploying `node_exporter` for host metrics — rejected as heavier operationally for the current single-app scope, though it remains the upgrade path if fuller host coverage is needed.

**Run the observability stack as Docker Compose services scraping the app over `host.docker.internal`:**
- **Decision:** Add `prometheus`, `grafana`, and `alertmanager` services with persistent volumes; Prometheus scrapes the app's `/metrics`, Grafana reads Prometheus, and Prometheus forwards alerts to Alertmanager.
- **Rationale:** Reuses the existing Compose-based local environment, keeps the stack reproducible, and matches the plan's configuration.
- **Alternative considered:** A managed/hosted monitoring service — rejected for a local-first development platform; self-hosted keeps parity with the rest of the Dockerized stack.

**Threshold-based alert rules in Prometheus with Alertmanager routing:**
- **Decision:** Define `HighRequestLatency`, `HighErrorRate`, and `LowMemory` rules with `for` durations and severities in `alerts.yml`, routed to a default receiver in `alertmanager.yml`.
- **Rationale:** Straightforward, transparent, and adequate for current needs; `for` durations suppress transient spikes.
- **Alternative considered:** Grafana-managed alerting — rejected to keep alert definitions versioned alongside the Prometheus config as code, though Grafana alerting remains available for dashboard-driven alerts later.

## Risks / Trade-offs

- **Metric label cardinality explosion** (e.g. per-user or per-id labels) → Restrict labels to bounded dimensions (status, method, endpoint template); rely on the instrumentator's untemplated-path grouping to avoid unbounded route labels.
- **Duplicate collector registration** (same metric name registered twice) → Funnel all custom collectors through `MetricsConfig` and initialize once at startup; avoid re-instantiating collectors per request.
- **`psutil` disk/CPU calls add per-scrape overhead** → Acceptable at the configured scrape interval; if it becomes hot, cache values or move host metrics to `node_exporter`.
- **`host.docker.internal` scrape target is platform-dependent** → Documented for local Docker Desktop; on Linux hosts the target/extra_hosts must be adjusted, called out in the compose notes.
- **Default Grafana and SMTP credentials are placeholders** → Flagged as non-production; must be replaced with secrets before any shared or production deployment.
- **Instrumentation added to services could alter behavior if it raises** → Metric recording must be side-effect-free and never fail the business operation; wrap or guard so a metrics error cannot break a request.
- **Alert noise / flapping** → Tune thresholds and `for` durations; start conservative and refine against observed baselines.

## Migration Plan

1. Add `prometheus-client`, `prometheus-fastapi-instrumentator`, and `psutil` to `pyproject.toml` and install.
2. Attach the instrumentator in `energyhub/main.py`, expose `/metrics`, add the `application_info` metric, and verify `curl /metrics` returns data.
3. Add `shared/infrastructure/metrics/` (`MetricsConfig`, `BusinessMetrics`, system metrics) and instrument services at business-event points.
4. Add the `prometheus` service and `prometheus/prometheus.yml`; bring it up and confirm the `energyhub` target is UP.
5. Add the `grafana` service, provision the Prometheus data source, and build/import the application, business, and infrastructure dashboards.
6. Add `alerts.yml`, wire `rule_files`/`alerting` in `prometheus.yml`, add the `alertmanager` service with `alertmanager.yml`, and verify rules load and route.
7. Rollback: the app-side change is additive (metrics only); reverting the branch removes the metrics module and instrumentation, and `docker-compose down` removes the observability services without touching application data.

## Open Questions

- Should host resource metrics stay in-process via `psutil`, or move to a dedicated `node_exporter` once more than one host/service needs coverage? (Current plan: in-process `psutil`.)
- Which notification channel is authoritative for production (email vs. Slack vs. webhook), and where do those secrets live? (Deferred; placeholder receiver now.)
- What are the final alert thresholds and `for` durations for latency, error rate, and memory once real baselines exist? (Plan values are starting points to tune.)
- Should the `/metrics` endpoint be access-restricted (network policy or auth) rather than open, given it exposes operational detail? (Deferred; open on the internal network for now.)
