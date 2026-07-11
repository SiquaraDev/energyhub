## Why

Earlier phases built the EnergyHub application and its runtime dependencies (PostgreSQL, Redis, RabbitMQ, Kafka, Elasticsearch, and the monitoring stack), but running the system still requires installing and wiring every service by hand on the host, and nothing packages the application itself. This phase containerizes the application and orchestrates the full dependency stack with Docker and Docker Compose, so the platform boots identically — with one command — in local, CI, and deployment environments.

## What Changes

- Add a multi-stage `Dockerfile`: a build stage that installs Poetry and production dependencies, and a slim runtime stage that runs as a non-root `appuser`, exposes port `8000`, and starts the app via `uvicorn energyhub.main:app`. Add a `.dockerignore` to keep the build context minimal and reproducible.
- Add/complete `docker-compose.yml` defining the `energyhub-api` service alongside PostgreSQL, Redis, RabbitMQ, Elasticsearch, Kafka + Zookeeper, Prometheus, and Grafana, all attached to a shared bridge network with `restart: unless-stopped`.
- Inject every runtime setting through environment variables (`DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `SECRET_KEY`, `ENVIRONMENT`) so a single image runs unchanged across environments (twelve-factor configuration).
- Gate API startup on dependency readiness using `depends_on` conditions backed by per-service `healthcheck` definitions.
- Declare named volumes for every stateful service (PostgreSQL, Redis, RabbitMQ, Elasticsearch, Prometheus, Grafana) so data survives container recreation.
- Containerize the messaging/streaming tier (RabbitMQ with its management UI, Kafka with Zookeeper) and the observability tier (Prometheus scrape config + Grafana), each with health checks and correct startup ordering.
- Establish an end-to-end validation workflow: bring the stack up, confirm every service is healthy, run an integration smoke test, and verify data persistence across a shutdown/startup cycle.

## Capabilities

### New Capabilities

- `application-container-image`: Multi-stage `Dockerfile` producing a slim, non-root runtime image that starts the API, plus a `.dockerignore` that minimizes the build context.
- `service-orchestration`: A `docker-compose.yml` that defines all services on a shared bridge network with restart policies and health-gated startup ordering via `depends_on` conditions.
- `container-configuration`: Twelve-factor, environment-variable-driven configuration and service credentials injected into containers so the same image runs in any environment.
- `data-persistence-volumes`: Named Docker volumes for every stateful service, ensuring data survives container recreation and full stack restarts.
- `messaging-and-streaming-containers`: Containerized RabbitMQ (broker + management UI) and Kafka + Zookeeper (streaming) services with health checks and dependency ordering.
- `observability-stack-containers`: Containerized Prometheus (with a mounted scrape config) and Grafana, ordered so Grafana starts after Prometheus.
- `environment-validation`: An end-to-end validation workflow confirming the full stack boots healthy, passes an integration smoke test, and preserves data across shutdown/startup.

### Modified Capabilities

None — this phase introduces the containerization and orchestration layer; it does not change any previously specified requirement.

## Impact

- **Dependencies**: Requires Docker Engine and Docker Compose on the host. Pulls base images `python:3.12-slim`, `postgres:16-alpine`, `redis:7-alpine`, `rabbitmq:3-management-alpine`, `docker.elastic.co/elasticsearch/elasticsearch:8.11.0`, `confluentinc/cp-kafka:7.5.0`, `confluentinc/cp-zookeeper:7.5.0`, `prom/prometheus:latest`, and `grafana/grafana:latest`.
- **New artifacts**: `Dockerfile`, `.dockerignore`, `docker-compose.yml`, and `prometheus/prometheus.yml` at the project root.
- **Consumes**: The application entrypoint `energyhub.main:app` and the `pyproject.toml` / `poetry.lock` dependency lockfiles from earlier phases, plus `energyhub.config.settings`, which must read its values from environment variables.
- **Provides**: A reproducible, one-command full-stack environment for development, CI, and deployment — the foundation for Fase 15 (Microservices).
- **Security**: The default service credentials and `SECRET_KEY` in `docker-compose.yml` are development placeholders and MUST be rotated and externalized (secrets manager / `.env`) before any production use.
