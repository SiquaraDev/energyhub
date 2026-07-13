# test-automation-workflow Specification

## Purpose
TBD - created by archiving change implement-fase-17. Update Purpose after archive.
## Requirements
### Requirement: Test workflow with database and cache service containers

The system SHALL provide a GitHub Actions workflow at `.github/workflows/test.yml` that provisions a PostgreSQL service container and a Redis service container, each with a health check, so integration tests run against real backing services.

#### Scenario: Service containers are healthy before tests

- **WHEN** the test job starts
- **THEN** the Postgres and Redis service containers are started and their health checks pass before the test steps run

### Requirement: Test workflow trigger coverage

The test workflow SHALL run on `push` to `main`, `develop`, and `feature/*` branches and on `pull_request` targeting `main` and `develop`.

#### Scenario: Feature branch push runs the tests

- **WHEN** a commit is pushed to a `feature/*` branch
- **THEN** the test workflow is triggered so work-in-progress is validated

### Requirement: Separate unit and integration test execution

The test job SHALL run the unit suite (`tests/unit`) and the integration suite (`tests/integration`) as distinct steps, and the integration step SHALL receive `DATABASE_URL` and `REDIS_URL` pointing at the service containers.

#### Scenario: Integration tests connect to service containers

- **WHEN** the integration test step runs
- **THEN** `DATABASE_URL` and `REDIS_URL` are set to the Postgres and Redis service endpoints and the integration tests execute against them

#### Scenario: Unit tests run independently of services

- **WHEN** the unit test step runs
- **THEN** it executes the `tests/unit` suite without requiring the integration environment variables

### Requirement: Test results uploaded regardless of outcome

The test job SHALL upload test/coverage results as a build artifact even when a prior step fails, so results are available for inspection on failed runs.

#### Scenario: Artifacts uploaded after a failing test run

- **WHEN** a test step fails
- **THEN** the results artifact is still uploaded (the upload step runs with `if: always()`)

