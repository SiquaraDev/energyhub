## 1. Application Container Image

- [ ] 1.1 Create a multi-stage `Dockerfile`: build stage on `python:3.12-slim` installing Poetry and `poetry install --only main` against copied `pyproject.toml`/`poetry.lock`
- [ ] 1.2 Add the runtime stage on `python:3.12-slim` copying only site-packages, bin, and application code from the build stage
- [ ] 1.3 Create a non-root `appuser`, `chown` the app directory to it, and switch to `USER appuser`
- [ ] 1.4 Add `EXPOSE 8000` and set `CMD` to `uvicorn energyhub.main:app --host 0.0.0.0 --port 8000`
- [ ] 1.5 Create `.dockerignore` excluding `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `htmlcov/`, `.coverage`, `.env`, and editor/config dirs
- [ ] 1.6 Build the image (`docker build -t energyhub:latest .`) and confirm it completes without error
- [ ] 1.7 Run the image standalone (`docker run -p 8000:8000 energyhub:latest`) and confirm the API serves on port 8000

## 2. Service Orchestration

- [ ] 2.1 Create `docker-compose.yml` with a shared `energyhub-network` bridge network
- [ ] 2.2 Define the `energyhub-api` service built from the `Dockerfile`, publishing port 8000, with `restart: unless-stopped`
- [ ] 2.3 Define the PostgreSQL, Redis, RabbitMQ, and Elasticsearch services attached to the shared network with `restart: unless-stopped`
- [ ] 2.4 Add per-service `healthcheck` blocks (`pg_isready`, `redis-cli ping`, `rabbitmq-diagnostics ping`, Elasticsearch cluster-health curl)
- [ ] 2.5 Add `depends_on` conditions on the API so it starts only after health-checked dependencies report healthy
- [ ] 2.6 Bring the stack up (`docker-compose up -d`) and confirm `docker-compose ps` lists all services running

## 3. Container Configuration

- [ ] 3.1 Inject `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `SECRET_KEY`, and `ENVIRONMENT` into the API service environment
- [ ] 3.2 Ensure all connection URLs address dependencies by Compose service name (not `localhost`)
- [ ] 3.3 Supply stateful-service credentials via env vars (`POSTGRES_USER`/`POSTGRES_PASSWORD`, `RABBITMQ_DEFAULT_USER`/`RABBITMQ_DEFAULT_PASS`)
- [ ] 3.4 Verify no connection strings or secrets are hard-coded in the image, and document the defaults as development placeholders to rotate before production
- [ ] 3.5 Confirm the API reads its settings from the injected environment by hitting a config-dependent endpoint

## 4. Data Persistence Volumes

- [ ] 4.1 Declare named volumes for `postgres_data`, `redis_data`, `rabbitmq_data`, and `elasticsearch_data`
- [ ] 4.2 Mount each named volume at the service's data path (e.g. `/var/lib/postgresql/data`)
- [ ] 4.3 Enable Redis append-only persistence (`redis-server --appendonly yes`)
- [ ] 4.4 Write data to PostgreSQL and Redis, run `docker-compose down` then `docker-compose up -d`, and confirm the data still exists

## 5. Messaging and Streaming Containers

- [ ] 5.1 Confirm the RabbitMQ service exposes ports 5672 (AMQP) and 15672 (management UI) and log in to the UI with the configured credentials
- [ ] 5.2 Add the Zookeeper service (`cp-zookeeper:7.5.0`) on the shared network
- [ ] 5.3 Add the Kafka service (`cp-kafka:7.5.0`) with `depends_on: zookeeper`, `KAFKA_ZOOKEEPER_CONNECT`, advertised listeners, and port 9092
- [ ] 5.4 Bring up the streaming services (`docker-compose up -d zookeeper kafka`) and confirm Kafka connects to Zookeeper in the logs
- [ ] 5.5 List topics (`kafka-topics --list --bootstrap-server localhost:9092`) to confirm the broker is operational

## 6. Observability Stack Containers

- [ ] 6.1 Create `prometheus/prometheus.yml` scrape configuration
- [ ] 6.2 Define the Prometheus service mounting `prometheus/prometheus.yml`, persisting to a `prometheus_data` volume, exposing port 9090
- [ ] 6.3 Define the Grafana service with `depends_on: prometheus`, admin credentials via env vars, a `grafana_data` volume, and port 3000
- [ ] 6.4 Confirm Prometheus loads its config on port 9090 and Grafana is reachable on port 3000 after Prometheus

## 7. Environment Validation

- [ ] 7.1 Bring up the full stack (`docker-compose up -d`) and wait for all services to report healthy in `docker-compose ps`
- [ ] 7.2 Confirm the API `/health` endpoint responds successfully inside the stack
- [ ] 7.3 Run the end-to-end smoke test: create a user, a client, and a contract, and verify cache, messaging, and search participation
- [ ] 7.4 Inspect `docker-compose logs` to confirm no service reports errors on startup
- [ ] 7.5 Cycle the stack (`docker-compose down` then `docker-compose up -d`) and confirm data persists and all services return healthy

## 8. Change Validation

- [ ] 8.1 Run `openspec validate implement-fase-14` and confirm the change is valid
