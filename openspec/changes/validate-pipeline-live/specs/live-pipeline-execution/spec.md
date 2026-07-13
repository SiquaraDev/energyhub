## ADDED Requirements

### Requirement: First live end-to-end pipeline run on GitHub-hosted runners

The system SHALL execute the `Build`, `Test`, `Docker`, and combined `CI/CD Pipeline` workflows for real on GitHub-hosted `ubuntu-latest` runners via a push to `master`, and each of the four workflow runs SHALL complete with a green (success) conclusion.

#### Scenario: All four workflows conclude green on a push to master

- **WHEN** a commit is pushed to `master` and the four workflows are triggered
- **THEN** the `Build`, `Test`, `Docker`, and `CI/CD Pipeline` runs each finish with conclusion `success` on GitHub-hosted runners

#### Scenario: The runs are tied to a single commit

- **WHEN** the validation push completes
- **THEN** all four workflow runs reference the same commit SHA, giving one auditable evidence trail

### Requirement: Build stage builds the package and passes the coverage gate

The live `Build` run SHALL install Poetry with Python 3.12, run `poetry build`, and execute the test suite with coverage such that the embedded 80% coverage gate passes and the job succeeds.

#### Scenario: Build and coverage gate pass live

- **WHEN** the `Build` workflow runs on the runner
- **THEN** `poetry build` succeeds and `pytest --cov` reports coverage at or above the 80% gate, so the job concludes green

### Requirement: Test stage runs the integration suite against real service containers

The live `Test` run (and the `build-and-test` job of the combined pipeline) SHALL provision Postgres 16 and Redis 7 as health-checked service containers, apply the database schema via `alembic upgrade head`, and run the skip-guarded integration step against those containers rather than a dead endpoint.

#### Scenario: Integration step executes against provisioned services

- **WHEN** the integration step runs after the Alembic migration
- **THEN** the suite connects to the Postgres/Redis service containers and the integration tests execute (not skipped) with the job concluding green

#### Scenario: Schema is applied before integration tests

- **WHEN** the migration step has run
- **THEN** the integration tests query an initialized schema and do not fail with "relation does not exist"

### Requirement: Combined pipeline enforces ordered stages live

The combined `CI/CD Pipeline` run SHALL execute its stages in the order `build-and-test` → `build-and-push` → `deploy`, enforced by job `needs`, with later stages starting only after earlier stages succeed.

#### Scenario: Stages run in dependency order

- **WHEN** the combined pipeline runs to completion green
- **THEN** `build-and-push` starts only after `build-and-test` succeeds and `deploy` starts only after `build-and-push` succeeds

#### Scenario: A failing early stage stops the pipeline

- **WHEN** the `build-and-test` stage fails on a run
- **THEN** the `build-and-push` and `deploy` jobs do not execute
