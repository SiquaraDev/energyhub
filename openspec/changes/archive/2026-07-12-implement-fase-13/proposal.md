## Why

Fases 1–12 built the full stack — persistence, use cases, API, messaging, and observability — but there is no automated test suite proving any of it works or guarding it against regressions. Before containerization (Fase 14) and any further change, the platform needs a repeatable, deterministic test suite with an enforced coverage floor so business logic, persistence, and endpoints stay correct as the codebase grows.

## What Changes

- Add the test toolchain as dev dependencies (`pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, `testcontainers`) and the `[tool.pytest.ini_options]` configuration in `pyproject.toml` (test paths, discovery patterns, async mode, default `addopts`).
- Add unit tests for the application-layer services (`UserService`, `ClientService`, and the remaining services) that isolate the unit under test with mocked collaborators and cover both happy paths and domain-exception paths, following a `test_should_...` naming convention.
- Add shared fixtures and test doubles in `tests/conftest.py` for external dependencies (`email_service`, `notification_service`, `event_producer`) so services can be exercised without real infrastructure.
- Add integration tests that run against a real, disposable PostgreSQL: repository tests via Testcontainers (`PostgresContainer`) and API tests via FastAPI `TestClient` with an authenticated token, asserting persisted state and HTTP responses.
- Add a `docker-compose.test.yml` (test PostgreSQL, Redis, RabbitMQ on non-default ports) and the session-scoped environment configuration that points the suite at the test infrastructure.
- Add coverage measurement and an 80% quality gate: `[tool.coverage.run]`/`[tool.coverage.report]` configuration (source, omissions, `fail_under = 80`), HTML and terminal reports, and `--cov-fail-under=80` in `addopts`.
- Run the full suite, triage failures into code/test/configuration bugs, fix them, document the fixes, and drive the suite to green.

## Capabilities

### New Capabilities

- `test-tooling-configuration`: Test dependencies and the `pytest` configuration (test paths, discovery patterns, async mode, default `addopts`) that make the suite runnable with a single command.
- `unit-testing`: Isolated unit tests for application-layer services using mocked collaborators, covering success and domain-exception paths under a consistent naming convention.
- `test-doubles-and-fixtures`: Shared `conftest.py` fixtures and mocks for external dependencies so units and services are testable without real infrastructure.
- `integration-testing`: Testcontainers-backed repository tests and FastAPI `TestClient` API tests that exercise the stack against a real, disposable database.
- `test-environment`: A `docker-compose.test.yml` and session-scoped environment configuration providing isolated PostgreSQL, Redis, and RabbitMQ instances for the suite.
- `coverage-quality-gate`: Coverage collection, HTML/terminal reporting, and an enforced 80% minimum that fails the build when unmet.
- `test-stabilization`: A repeatable triage-and-fix loop that classifies failures, corrects the underlying bug, documents it, and confirms the whole suite passes.

### Modified Capabilities

None — this phase adds the test suite and its tooling; it changes no previously specified application requirement.

## Impact

- **Dependencies**: Adds dev-only `pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, and `testcontainers` to the `dev` Poetry group. No production dependency changes.
- **Consumes**: The services and DTOs from Fase 6–7, repositories from Fase 5, the FastAPI app (`energyhub.main:app`) and auth flow from Fase 8+, and the schema/migrations from Fase 4.
- **Provides**: A `tests/` tree mirroring the module structure, a shared `tests/conftest.py`, a `docker-compose.test.yml`, and an enforced coverage gate that later phases (Fase 14+) build on in CI.
- **New artifacts**: `tests/**` (unit and integration tests, fixtures), `docker-compose.test.yml`, and the `[tool.pytest.ini_options]`, `[tool.coverage.run]`, and `[tool.coverage.report]` sections plus dev dependencies in `pyproject.toml`.
- **Environment**: Integration tests require Docker to be available (Testcontainers spins up ephemeral containers); unit tests run without it. Test infrastructure uses non-default ports (5433/6380/5673) to avoid colliding with local development services.
