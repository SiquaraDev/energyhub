# test-tooling-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-13. Update Purpose after archive.
## Requirements
### Requirement: Test dependencies

The project SHALL declare `pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, and `testcontainers` in the `dev` Poetry dependency group so the suite installs with `poetry install` and none of them ship as production dependencies.

#### Scenario: Test toolchain is available after install

- **WHEN** a developer runs `poetry install` on a clean checkout
- **THEN** `pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, and `testcontainers` are installed in the environment and available to `poetry run pytest`

#### Scenario: Test dependencies stay out of the production set

- **WHEN** the project is installed without dev dependencies (`poetry install --without dev` or an equivalent production build)
- **THEN** none of the test-only packages are present in the resulting environment

### Requirement: Pytest configuration

The project SHALL configure `pytest` under `[tool.pytest.ini_options]` in `pyproject.toml` with `testpaths` pointing at `tests`, discovery patterns for files/classes/functions, asyncio mode enabled, and default `addopts` so the suite runs consistently from a single command.

#### Scenario: Suite is discovered and runnable with one command

- **WHEN** `poetry run pytest` is executed from the project root with no extra arguments
- **THEN** pytest collects tests only under `tests` using the configured discovery patterns and applies the default `addopts`

#### Scenario: Async tests execute without per-test markers configured elsewhere

- **WHEN** an `async def test_...` function is collected
- **THEN** the configured asyncio mode runs it as a coroutine without raising an "async test not natively supported" error

