## Context

By the end of Fase 12 the platform is functionally complete — persistence (Fase 5), use cases and services (Fase 6–7), the FastAPI surface and auth (Fase 8+), messaging, and observability — but it has no automated tests. There is nothing to catch a regression, and no evidence that the layers behave as specified. This phase adds the test suite before containerization (Fase 14), so the pipeline that ships images is guarding verified code.

The stack constrains the approach: SQLAlchemy 2.x async, FastAPI/Pydantic, Python ≥3.12, Poetry for dependency management. The application follows Clean Architecture (domain / application / infrastructure / presentation), which makes the application-layer services the natural unit-test seam and the repositories/routers the natural integration seam. The test toolchain is fixed by the plan: `pytest` with `pytest-asyncio` for coroutine tests, `pytest-mock` for doubles, `pytest-cov` for coverage, and `testcontainers` for a real, disposable PostgreSQL. Docker must be available for the integration tier; unit tests run without it.

## Goals / Non-Goals

**Goals:**
- Make the suite installable and runnable with a single command via `pyproject.toml` configuration.
- Unit-test application services in isolation with mocked collaborators, covering success and domain-exception paths.
- Provide shared `conftest.py` fixtures/doubles for external dependencies (email, notifications, events).
- Integration-test repositories against a real PostgreSQL (Testcontainers) and endpoints through FastAPI `TestClient`.
- Provide a `docker-compose.test.yml` and session-scoped environment wiring for isolated test infrastructure.
- Measure coverage and enforce an 80% floor that fails the run when unmet.
- Drive the suite to green, fixing (not hiding) the defects it surfaces.

**Non-Goals:**
- No new application features, endpoints, or schema changes — this phase only tests existing behavior.
- No CI pipeline definition (that is wired in Fase 14+); this phase provides the gate the pipeline will invoke.
- No load, performance, security, or contract testing beyond functional correctness.
- No 100% coverage mandate — 80% is the floor, not a target to game with trivial tests.

## Decisions

**Unit tests target the application-layer services with mocked collaborators:**
- **Decision:** Unit tests construct a service (e.g. `UserService`, `ClientService`) directly, passing `Mock`/`AsyncMock` repositories, mappers, and external services; no database, broker, or app wiring is involved.
- **Rationale:** The service layer is where business rules live and is the cheapest, most stable seam to assert them; mocking collaborators keeps unit tests fast and deterministic and pins the test to one unit.
- **Alternative considered:** Testing business rules only through the API layer — rejected; end-to-end tests are slower, couple many concerns, and give poor localization when a rule breaks.

**`AsyncMock` for async collaborators, `Mock` for sync, with `pytest-asyncio`:**
- **Decision:** Async collaborators (repositories, external async services) are `AsyncMock`; synchronous ones (mappers) are plain `Mock`; async tests are marked/collected via `pytest-asyncio`'s configured mode.
- **Rationale:** The codebase is async end-to-end; awaiting a plain `Mock` raises, and `AsyncMock` makes awaited calls resolve to configured return values while still recording interactions for assertions.
- **Alternative considered:** Hand-rolled fake coroutines/stubs — rejected as boilerplate that `AsyncMock` already provides, including call assertions.

**Integration tests use Testcontainers rather than a shared standing database:**
- **Decision:** Repository integration tests spin up an ephemeral `PostgresContainer` per test module, build an async engine against it, and dispose it at module teardown; per-test isolation is achieved with transaction rollback or truncation.
- **Rationale:** A disposable, real PostgreSQL exercises actual SQL, types, and constraints (which SQLite or an in-memory fake would not), and per-module scope amortizes container startup cost while keeping tests hermetic and reproducible on any machine with Docker.
- **Alternative considered:** A single long-lived, developer-managed test database — rejected; it drifts, leaks state between runs, and is not reproducible in CI. `docker-compose.test.yml` is still provided as a convenience for manual/local runs, but the automated repository tests own their container lifecycle.

**API tests go through FastAPI `TestClient` with a real login:**
- **Decision:** Endpoint tests use `TestClient(app)`, first calling the login endpoint to obtain a JWT and then sending it as a bearer token on protected routes, asserting status codes and response bodies.
- **Rationale:** Exercises routing, dependency injection, serialization, and the auth middleware together — the behaviors that unit tests deliberately skip — with assertions at the HTTP contract level.
- **Alternative considered:** Bypassing auth by overriding the security dependency — rejected as the default; going through the real login path validates the auth flow, though dependency overrides remain available for narrowly focused cases.

**Test infrastructure is isolated on non-default ports and pointed at via session env:**
- **Decision:** `docker-compose.test.yml` binds PostgreSQL/Redis/RabbitMQ to 5433/6380/5673, and a session-scoped, autouse fixture sets `DATABASE_URL`/`REDIS_URL`/`RABBITMQ_URL` to those endpoints before app config loads.
- **Rationale:** Prevents collisions with local development services and guarantees the suite can never accidentally touch a development or production datastore.
- **Alternative considered:** Reusing the development compose services on default ports — rejected; it risks polluting or destroying dev data and makes parallel dev/test impossible.

**Coverage is enforced as a gate, single-sourced in `pyproject.toml`:**
- **Decision:** `--cov=energyhub --cov-fail-under=80` lives in `addopts`, with `[tool.coverage.run]` scoping `source`/`omit` and `[tool.coverage.report]` setting `fail_under = 80`; reports are HTML + terminal.
- **Rationale:** Making the threshold part of the default invocation means every run (local and CI) enforces it identically, with no separate command to remember; omitting `main.py`/`__init__.py`/tests keeps the percentage meaningful.
- **Alternative considered:** Enforcing coverage only in CI via a bespoke script — rejected; it lets local runs pass while CI fails and splits the source of truth for the threshold.

## Risks / Trade-offs

- **Docker unavailable in some environments** → Integration tests fail to start containers. Keep the unit tier fully runnable without Docker, and document that the integration tier requires Docker; allow selecting tiers by path/marker.
- **Container startup slows the suite** → Module-scoped containers and reuse within a module amortize the cost; keep integration tests focused on behaviors that genuinely need a database rather than duplicating unit coverage.
- **Flaky async/integration tests from shared state** → Enforce per-test isolation (rollback/truncate) and avoid cross-test ordering dependencies so runs are deterministic.
- **Coverage gate encourages low-value tests** → Treat 80% as a floor and review tests for meaningful assertions; the domain-exception and finder scenarios in the specs anchor coverage to real behavior, not line-hitting.
- **Application code not yet materialized** → The suite is authored against the module structure the earlier phases define; where a collaborator or DTO name differs at implementation time, tests are reconciled to the actual code, which remains the source of truth.
- **Test env variables leaking into a real datastore** → The autouse session fixture sets test endpoints before config load and non-default ports make accidental production/dev connections structurally unlikely; verify the app reads config lazily so the override takes effect.

## Migration Plan

1. Add the dev dependencies and `[tool.pytest.ini_options]` to `pyproject.toml`; confirm `poetry run pytest` collects an empty/placeholder suite cleanly.
2. Add `tests/conftest.py` with the shared external-dependency fixtures and the session-scoped environment configuration.
3. Write service unit tests (`UserService`, `ClientService`, then the remaining services) covering happy and exception paths.
4. Add `docker-compose.test.yml`; add repository integration tests using Testcontainers and API tests via `TestClient`.
5. Add the `[tool.coverage.run]`/`[tool.coverage.report]` configuration and `--cov-fail-under=80`; generate HTML/terminal reports.
6. Run the full suite, triage and fix failures, document the bugs fixed, and iterate until green with coverage ≥ 80%.
7. Rollback: this phase is additive (tests, compose file, `pyproject.toml` config); reverting the branch removes the suite without affecting application behavior.

## Open Questions

- Should integration tests be gated behind a pytest marker (e.g. `@pytest.mark.integration`) so `pytest -m "not integration"` runs Docker-free, or is directory-based selection sufficient? (Leaning toward a marker for CI ergonomics.)
- Is 80% the right long-term floor, or should it ratchet upward as coverage matures once the codebase is materialized?
- For API tests, prefer the real login path or a dependency-override auth stub as the default? (Current plan: real login for the primary path, overrides only for narrowly scoped cases.)
- Which shared infrastructure (Redis/RabbitMQ) actually needs a live test container versus a double, given most service logic is unit-tested with mocks?
