## Context

By this phase the EnergyHub application and all of its runtime dependencies exist, but they are assumed to be installed and configured directly on the developer's host. There is no image for the application itself and no single definition that reproduces the full topology — API, PostgreSQL, Redis, RabbitMQ, Kafka/Zookeeper, Elasticsearch, Prometheus, and Grafana. That makes onboarding, CI, and deployment brittle and environment-specific, which contradicts the phase objective of running the system in any environment.

This phase adds a containerization and orchestration layer on top of the existing code without changing application behavior. The stack is fixed by the plan: a Poetry-managed Python 3.12 app, a multi-stage `Dockerfile`, and a `docker-compose.yml` that wires every service on one bridge network. Configuration is single-sourced through environment variables so a single image is portable. The database schema, messaging, search, and monitoring concerns were established in earlier phases; here they are only packaged and orchestrated, not redesigned.

## Goals / Non-Goals

**Goals:**
- Produce a slim, reproducible, non-root application image via a multi-stage `Dockerfile` and a `.dockerignore`.
- Orchestrate the full service stack with `docker-compose.yml`: one shared bridge network, restart policies, health checks, and health-gated startup ordering.
- Make the application twelve-factor: all configuration and secrets injected via environment variables, no connection strings baked into the image.
- Persist all stateful services on named volumes so data survives container recreation.
- Provide an end-to-end validation workflow (health, smoke test, persistence across restart).

**Non-Goals:**
- No application logic, schema, or feature changes — packaging only.
- No production orchestrator (Kubernetes/Swarm), autoscaling, or ingress/TLS termination — that is later work.
- No secrets-manager integration; Compose env values are development placeholders.
- No image registry/publishing pipeline or CI wiring beyond building locally.
- No performance tuning of the containerized services beyond sensible resource hints (e.g. Elasticsearch JVM heap).

## Decisions

**Multi-stage Dockerfile with a slim, non-root runtime:**
- **Decision:** A build stage installs Poetry and resolves `--only main` dependencies against `pyproject.toml`/`poetry.lock`; the runtime stage starts from `python:3.12-slim`, copies only site-packages and app code, creates `appuser`, and runs uvicorn as that user.
- **Rationale:** Keeps the final image small and free of build tooling, and running as non-root reduces the blast radius of a container compromise. Copying the lockfile first leverages Docker layer caching for fast rebuilds.
- **Alternative considered:** A single-stage image that installs Poetry and deps in place — rejected because it ships compilers and caches, bloats the image, and encourages running as root.

**Compose as the orchestration surface (not hand-run containers or an orchestrator):**
- **Decision:** Define the entire topology declaratively in one `docker-compose.yml` on a shared `energyhub-network` bridge, with `restart: unless-stopped` per service.
- **Rationale:** Compose matches the plan, gives one-command up/down, and reproduces the same topology everywhere while staying simple for local dev and CI.
- **Alternative considered:** Kubernetes manifests / Helm now — rejected as premature for this phase; it adds operational overhead before microservices (Fase 15) require it. Plain `docker run` scripts were also rejected as non-declarative and error-prone.

**Health-gated startup via `depends_on` conditions + per-service health checks:**
- **Decision:** Each dependency that can report readiness declares a `healthcheck` (e.g. `pg_isready`, `redis-cli ping`, `rabbitmq-diagnostics ping`, Elasticsearch cluster-health curl), and the API uses `depends_on: { condition: service_healthy }` for those.
- **Rationale:** Prevents the classic race where the API boots before PostgreSQL/Elasticsearch accept connections, so the stack converges without manual retries.
- **Alternative considered:** Application-side retry/backoff only — kept as a defensive fallback but rejected as the primary mechanism because health-gated ordering makes startup deterministic and easier to reason about.

**Twelve-factor configuration through environment variables:**
- **Decision:** Inject `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `SECRET_KEY`, and `ENVIRONMENT` at run time; connection URLs address dependencies by Compose service name, never `localhost`.
- **Rationale:** One image runs unchanged across environments, which is the core objective of the phase; it also keeps secrets out of the image layers.
- **Alternative considered:** Baking config files or defaults into the image — rejected because it couples the image to one environment and risks leaking secrets in image history.

**Named volumes for every stateful service:**
- **Decision:** Declare named volumes for PostgreSQL, Redis (append-only enabled), RabbitMQ, Elasticsearch, Prometheus, and Grafana, mounted at each service's data path.
- **Rationale:** Data must survive `docker-compose down`/`up`; named volumes are managed by Docker, portable, and clearer than host bind mounts for data directories.
- **Alternative considered:** Host bind mounts — rejected for data dirs because they introduce host-path and permission coupling; bind mounts are used only for read-only config like `prometheus.yml`.

**Pinned base image tags (with a documented exception):**
- **Decision:** Pin dependency images to specific versions (`postgres:16-alpine`, `redis:7-alpine`, `rabbitmq:3-management-alpine`, `elasticsearch:8.11.0`, `cp-kafka:7.5.0`, `cp-zookeeper:7.5.0`) per the plan; Prometheus and Grafana follow the plan's `latest`.
- **Rationale:** Pinning makes builds reproducible and avoids surprise breakage; matching the plan's tags keeps this phase aligned with the documented environment.
- **Alternative considered:** Pinning everything including Prometheus/Grafana — preferred long-term and noted as an open question, but this phase follows the plan to avoid drift.

## Risks / Trade-offs

- **Elasticsearch memory pressure in local/CI environments** → Constrain the JVM heap via `ES_JAVA_OPTS=-Xms512m -Xmx512m` and rely on its health check so dependents wait; document the memory requirement for small machines.
- **`latest` tags for Prometheus/Grafana drift over time** → Accept for this phase to match the plan; flagged as an open question to pin later for full reproducibility.
- **Default credentials and `SECRET_KEY` are insecure placeholders** → Documented as development-only; production MUST inject rotated secrets via `.env`/secrets manager. This is a deliberate, called-out trade-off, not an oversight.
- **Slow first startup while images pull and services become healthy** → Health-gated `depends_on` makes convergence deterministic; validation allows time for services to report healthy before asserting.
- **Kafka/Zookeeper advertised-listener misconfiguration** → Kafka only advertises `PLAINTEXT://localhost:9092` per the plan, which works for host access but can confuse in-network clients; validated by listing topics, and revisited if in-cluster producers are added.
- **Non-root user vs. mounted-volume permissions** → Ensure app files are `chown`ed to `appuser` in the image; data volumes are owned by their official images' users, so the API does not write to them directly.

## Migration Plan

1. Add the `Dockerfile` and `.dockerignore`; run `docker build -t energyhub:latest .` and a standalone `docker run -p 8000:8000` to confirm the image serves the API.
2. Author `docker-compose.yml` with the API plus PostgreSQL, Redis, RabbitMQ, and Elasticsearch, including health checks, `depends_on` conditions, the shared network, and named volumes.
3. Add the messaging/streaming services (Zookeeper + Kafka) and the observability services (Prometheus with mounted `prometheus/prometheus.yml`, Grafana), with correct ordering.
4. Bring the stack up (`docker-compose up -d`), confirm `docker-compose ps` shows all services healthy/running, and check API `/health`.
5. Run the end-to-end smoke test (user → client → contract, plus cache/messaging/search checks) and verify data persists across a `docker-compose down`/`up` cycle.
6. Rollback: this phase is additive and infrastructure-only — reverting the branch removes the container artifacts; `docker-compose down -v` tears down containers and volumes without touching application source.

## Open Questions

- Should Prometheus and Grafana be pinned to explicit versions rather than `latest` for full reproducibility? (Plan uses `latest`; recommend pinning in a follow-up.)
- Should a `docker-compose.override.yml` / `.env` split be introduced now to separate dev credentials from the committed base file, ahead of the production secrets story?
- Does CI need a slimmer compose profile (e.g. omit Grafana/Prometheus) to speed the smoke test, or is the full stack acceptable?
- Should a container-level `HEALTHCHECK` be added to the API image itself (in addition to Compose-level gating) so orchestrators can observe API readiness directly? (Deferred until Fase 15.)
