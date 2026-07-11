## ADDED Requirements

### Requirement: Build workflow triggered on push and pull request

The system SHALL provide a GitHub Actions workflow at `.github/workflows/build.yml` that runs on `push` to the `main` and `develop` branches and on `pull_request` targeting `main`.

#### Scenario: Workflow runs on a push to a protected branch

- **WHEN** a commit is pushed to `main` or `develop`
- **THEN** the build workflow is triggered and executes on an `ubuntu-latest` runner

#### Scenario: Workflow runs on a pull request

- **WHEN** a pull request is opened or updated against `main`
- **THEN** the build workflow is triggered so the change is validated before merge

### Requirement: Reproducible Python and Poetry environment

The build job SHALL check out the repository, set up Python 3.12, install Poetry, and install project dependencies with `poetry install --no-interaction` before any build or test step runs.

#### Scenario: Environment is prepared before build

- **WHEN** the build job starts
- **THEN** the code is checked out, Python 3.12 and Poetry are available, and dependencies are installed non-interactively prior to building

### Requirement: Package build and test execution

The build job SHALL run `poetry build` to produce the package artifact and SHALL execute the test suite via `poetry run pytest`; the job SHALL fail if either the build or the tests fail.

#### Scenario: Build and tests succeed

- **WHEN** the package builds and all tests pass
- **THEN** the build job completes successfully

#### Scenario: A failing test fails the job

- **WHEN** any test fails during the build job
- **THEN** the job reports failure and does not report a green build

### Requirement: Coverage report generation and upload

The build job SHALL generate a coverage report (`poetry run pytest --cov=energyhub --cov-report=xml`) and SHALL upload it to the coverage service.

#### Scenario: Coverage is produced and uploaded

- **WHEN** the test step runs with coverage enabled
- **THEN** a `coverage.xml` report is produced and uploaded to the configured coverage service
