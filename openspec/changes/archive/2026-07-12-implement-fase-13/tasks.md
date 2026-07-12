## 1. Test Tooling Configuration

- [x] 1.1 Add `pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, and `testcontainers` to the `dev` Poetry group and run `poetry install`
- [x] 1.2 Add `[tool.pytest.ini_options]` to `pyproject.toml` with `testpaths = ["tests"]` and `python_files`/`python_classes`/`python_functions` discovery patterns
- [x] 1.3 Enable asyncio mode for `pytest-asyncio` so `async def` tests run without per-test markers
- [x] 1.4 Create the `tests/` package tree mirroring the module structure and confirm `poetry run pytest` collects cleanly with no tests yet

## 2. Shared Fixtures and Test Environment

- [x] 2.1 Create `tests/conftest.py` with `AsyncMock` fixtures for `email_service`, `notification_service`, and `event_producer`
- [x] 2.2 Add a session-scoped `autouse` fixture that sets `DATABASE_URL`, `REDIS_URL`, and `RABBITMQ_URL` to the test endpoints before app config loads
- [x] 2.3 Confirm the shared doubles are awaitable and support interaction assertions (`assert_called_once`)

## 3. Unit Tests

- [x] 3.1 Add `tests/auth/application/service/test_user_service.py`: happy-path `create` asserting the response and a single `save` call
- [x] 3.2 Add `UserService` exception tests: username-exists and email-exists paths raise `UserAlreadyExistsException` and never call `save`
- [x] 3.3 Add `tests/clients/application/service/test_client_service.py`: happy-path `create` plus CNPJ-exists path raising `ClientAlreadyExistsException`
- [x] 3.4 Add unit tests for the remaining application services, mocking their collaborators
- [x] 3.5 Verify all unit tests follow the `test_should_<expected>_when_<condition>` naming convention and pass without Docker

## 4. Test Infrastructure

- [x] 4.1 Create `docker-compose.test.yml` with PostgreSQL, Redis, and RabbitMQ on non-default ports (5433/6380/5673)
- [x] 4.2 Start the stack with `docker-compose -f docker-compose.test.yml up -d` and confirm the services are reachable on the configured ports

## 5. Integration Tests

- [x] 5.1 Add a module-scoped `PostgresContainer` fixture and an async engine bound to it, disposed at module teardown
- [x] 5.2 Add a per-test isolation mechanism (transaction rollback or truncate) for the integration session
- [x] 5.3 Add `tests/clients/infrastructure/persistence/test_client_repository.py`: save + `find_by_id` and `find_by_cnpj` against the container
- [x] 5.4 Add `tests/clients/presentation/router/test_client_router.py`: obtain a token via login, POST a client, assert `201` and the response body
- [x] 5.5 Run the integration tests and confirm they pass against the Testcontainers PostgreSQL

## 6. Coverage Quality Gate

- [x] 6.1 Add `[tool.coverage.run]` scoping `source = ["energyhub"]` and omitting tests, `__init__.py`, and `main.py`
- [x] 6.2 Add `[tool.coverage.report]` with `fail_under = 80`
- [x] 6.3 Add `--cov=energyhub`, `--cov-report=html`, `--cov-report=term`, and `--cov-fail-under=80` to `addopts`
- [x] 6.4 Run `poetry run pytest --cov=energyhub --cov-report=html` and inspect `htmlcov/index.html` plus the terminal summary

## 7. Test Stabilization

- [x] 7.1 Run the full suite with `poetry run pytest` and collect all failures
- [x] 7.2 Triage each failure as a code, test, or configuration defect
- [x] 7.3 Fix the underlying cause of each failure without skipping or masking real defects
- [x] 7.4 Document the symptom, root cause, and fix for each bug corrected
- [x] 7.5 Re-run the suite until all tests pass and coverage is at least 80%

## 8. Validation

- [x] 8.1 Confirm unit tests run and pass without Docker
- [x] 8.2 Confirm integration tests pass against the Dockerized test infrastructure
- [x] 8.3 Confirm the run fails when coverage drops below 80% and passes at or above it
- [x] 8.4 Run `openspec validate implement-fase-13` and confirm the change is valid
