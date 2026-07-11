## 1. Dependencies and Setup

- [ ] 1.1 Add `prometheus-client`, `prometheus-fastapi-instrumentator`, and `psutil` to `pyproject.toml`
- [ ] 1.2 Install the dependencies (`poetry add prometheus-client prometheus-fastapi-instrumentator psutil`)
- [ ] 1.3 Create the `energyhub/shared/infrastructure/metrics/` package with an `__init__.py`

## 2. Metrics Instrumentation

- [ ] 2.1 Configure the Prometheus `Instrumentator` in `energyhub/main.py` with in-progress and latency tracking and `excluded_handlers=["/metrics"]`
- [ ] 2.2 Attach the instrumentator to `app` and expose it at the `/metrics` endpoint
- [ ] 2.3 Publish an `application_info` metric populated from `settings` (application name, environment, version)
- [ ] 2.4 Verify `curl http://localhost:8000/metrics` returns Prometheus-format output and default HTTP metrics

## 3. Custom Application Metrics

- [ ] 3.1 Create `MetricsConfig` in `shared/infrastructure/metrics/metrics_config.py` with factory methods for the client-created counter, contract-created counter (labeled by status), invoice-paid counter, active-clients gauge, and request-duration histogram
- [ ] 3.2 Create a `BusinessMetrics` helper that obtains collectors from `MetricsConfig` and initializes labeled counters/gauges to zero at startup
- [ ] 3.3 Add `increment_contract_created(status)`, `increment_invoice_paid()`, and `set_active_clients(count)` methods on `BusinessMetrics`
- [ ] 3.4 Instrument `ClientService.create` to time the operation via the request-duration histogram and increment `client_created_total`
- [ ] 3.5 Instrument the contract and invoice flows to record their business metrics at the point of the successful event
- [ ] 3.6 Ensure metric recording is side-effect-free and cannot fail the underlying business operation

## 4. System Resource Metrics

- [ ] 4.1 Create the memory, CPU, and disk gauges (`memory_usage_bytes`, `cpu_usage_percent`, `disk_usage_percent`) via `psutil` in `shared/infrastructure/metrics/`
- [ ] 4.2 Implement an `update_system_metrics()` routine that refreshes the gauges from `psutil` at collection time
- [ ] 4.3 Confirm the resource gauges appear on the `/metrics` endpoint with current host values

## 5. Prometheus Server and Scraping

- [ ] 5.1 Add the `prometheus` service to `docker-compose.yml` with a mounted config and a `prometheus_data` volume
- [ ] 5.2 Create `prometheus/prometheus.yml` with global scrape settings and an `energyhub` scrape job targeting the application `/metrics`
- [ ] 5.3 Start the container (`docker-compose up -d prometheus`) and confirm the `energyhub` target is UP at http://localhost:9090
- [ ] 5.4 Validate PromQL queries for a default metric and a custom metric (e.g. `client_created_total`, `rate(fastapi_request_duration_seconds_count[5m])`)

## 6. Grafana Dashboards

- [ ] 6.1 Add the `grafana` service to `docker-compose.yml` with admin env vars, a `grafana_data` volume, and `depends_on: prometheus`
- [ ] 6.2 Start Grafana (`docker-compose up -d grafana`) and configure the Prometheus data source at `http://prometheus:9090` (Save & Test)
- [ ] 6.3 Build the application dashboard (throughput, latency p50/p95/p99, error rate, Python resource usage)
- [ ] 6.4 Build the business dashboard (active clients, contracts by status, invoices issued vs paid)
- [ ] 6.5 Build the infrastructure dashboard (host resources, cache hit rate, Elasticsearch latency)
- [ ] 6.6 Import the community FastAPI (14314) and Python (10991) dashboards

## 7. Alerting

- [ ] 7.1 Create `prometheus/alerts.yml` with `HighRequestLatency`, `HighErrorRate`, and `LowMemory` rules including severities, `for` durations, and annotations
- [ ] 7.2 Wire `rule_files` and the `alerting` block into `prometheus.yml` pointing at Alertmanager
- [ ] 7.3 Add the `alertmanager` service to `docker-compose.yml` mounting `prometheus/alertmanager.yml`
- [ ] 7.4 Create `prometheus/alertmanager.yml` with a route and at least one receiver (email/Slack/webhook placeholder)
- [ ] 7.5 Reload Prometheus and confirm the rules appear on the rules page and route to Alertmanager

## 8. Validation

- [ ] 8.1 Confirm `/metrics` exposes default HTTP, custom business, and system resource metrics
- [ ] 8.2 Confirm Prometheus scrapes the application target and the metrics are queryable
- [ ] 8.3 Confirm the Grafana dashboards render and the alert rules load and route to Alertmanager
- [ ] 8.4 Run `openspec validate implement-fase-12` and confirm the change is valid
