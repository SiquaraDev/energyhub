## 1. Dependencies and Setup

- [x] 1.1 Add `prometheus-client`, `prometheus-fastapi-instrumentator`, and `psutil` to `pyproject.toml`
- [x] 1.2 Install the dependencies (`poetry add prometheus-client prometheus-fastapi-instrumentator psutil`)
- [x] 1.3 Create the `energyhub/shared/infrastructure/metrics/` package with an `__init__.py`

## 2. Metrics Instrumentation

- [x] 2.1 Configure the Prometheus `Instrumentator` in `energyhub/main.py` with in-progress and latency tracking and `excluded_handlers=["/metrics"]`
- [x] 2.2 Attach the instrumentator to `app` and expose it at the `/metrics` endpoint
- [x] 2.3 Publish an `application_info` metric populated from `settings` (application name, environment, version)
- [x] 2.4 Verify `curl http://localhost:8000/metrics` returns Prometheus-format output and default HTTP metrics

## 3. Custom Application Metrics

- [x] 3.1 Create `MetricsConfig` in `shared/infrastructure/metrics/metrics_config.py` with factory methods for the client-created counter, contract-created counter (labeled by status), invoice-paid counter, active-clients gauge, and request-duration histogram
- [x] 3.2 Create a `BusinessMetrics` helper that obtains collectors from `MetricsConfig` and initializes labeled counters/gauges to zero at startup
- [x] 3.3 Add `increment_contract_created(status)`, `increment_invoice_paid()`, and `set_active_clients(count)` methods on `BusinessMetrics`
- [x] 3.4 Instrument `ClientService.create` to time the operation via the request-duration histogram and increment `client_created_total`
- [x] 3.5 Instrument the contract and invoice flows to record their business metrics at the point of the successful event
- [x] 3.6 Ensure metric recording is side-effect-free and cannot fail the underlying business operation

## 4. System Resource Metrics

- [x] 4.1 Create the memory, CPU, and disk gauges (`memory_usage_bytes`, `cpu_usage_percent`, `disk_usage_percent`) via `psutil` in `shared/infrastructure/metrics/`
- [x] 4.2 Implement an `update_system_metrics()` routine that refreshes the gauges from `psutil` at collection time
- [x] 4.3 Confirm the resource gauges appear on the `/metrics` endpoint with current host values

## 5. Prometheus Server and Scraping

- [x] 5.1 Add the `prometheus` service to `docker-compose.yml` with a mounted config and a `prometheus_data` volume
- [x] 5.2 Create `prometheus/prometheus.yml` with global scrape settings and an `energyhub` scrape job targeting the application `/metrics`
- [x] 5.3 Start the container (`docker-compose up -d prometheus`) and confirm the `energyhub` target is UP at http://localhost:9090
- [x] 5.4 Validate PromQL queries for a default metric and a custom metric (e.g. `client_created_total`, `rate(fastapi_request_duration_seconds_count[5m])`)

## 6. Grafana Dashboards

- [x] 6.1 Add the `grafana` service to `docker-compose.yml` with admin env vars, a `grafana_data` volume, and `depends_on: prometheus`
- [x] 6.2 Start Grafana (`docker-compose up -d grafana`) and configure the Prometheus data source at `http://prometheus:9090` (Save & Test)
- [x] 6.3 Build the application dashboard (throughput, latency p50/p95/p99, error rate, Python resource usage)
- [x] 6.4 Build the business dashboard (active clients, contracts by status, invoices issued vs paid)
- [x] 6.5 Build the infrastructure dashboard (host resources, cache hit rate, Elasticsearch latency)
- [x] 6.6 Import the community FastAPI (14314) and Python (10991) dashboards

## 7. Alerting

- [x] 7.1 Create `prometheus/alerts.yml` with `HighRequestLatency`, `HighErrorRate`, and `LowMemory` rules including severities, `for` durations, and annotations
- [x] 7.2 Wire `rule_files` and the `alerting` block into `prometheus.yml` pointing at Alertmanager
- [x] 7.3 Add the `alertmanager` service to `docker-compose.yml` mounting `prometheus/alertmanager.yml`
- [x] 7.4 Create `prometheus/alertmanager.yml` with a route and at least one receiver (email/Slack/webhook placeholder)
- [x] 7.5 Reload Prometheus and confirm the rules appear on the rules page and route to Alertmanager

## 8. Validation

- [x] 8.1 Confirm `/metrics` exposes default HTTP, custom business, and system resource metrics
- [x] 8.2 Confirm Prometheus scrapes the application target and the metrics are queryable
- [x] 8.3 Confirm the Grafana dashboards render and the alert rules load and route to Alertmanager
- [x] 8.4 Run `openspec validate implement-fase-12` and confirm the change is valid
