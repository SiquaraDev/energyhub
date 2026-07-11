## ADDED Requirements

### Requirement: Per-service Docker image build via a matrix

The system SHALL provide a GitHub Actions workflow at `.github/workflows/docker.yml` that builds one Docker image per service using a build matrix covering `auth-service`, `client-service`, `contract-service`, `financial-service`, `audit-service`, and `api-gateway`.

#### Scenario: Each service builds in its own matrix job

- **WHEN** the Docker workflow runs
- **THEN** a separate build job runs for each service in the matrix, using that service's `Dockerfile` under `./services/<service>/`

### Requirement: Buildx-based builds

The Docker workflow SHALL set up Docker Buildx and build each image with `docker/build-push-action` using the service directory as build context.

#### Scenario: Buildx is initialized before building

- **WHEN** a matrix build job starts
- **THEN** Docker Buildx is set up before the build-and-push step executes

### Requirement: Registry-backed layer caching

The Docker workflow SHALL configure registry-backed layer caching via `cache-from` and `cache-to` so unchanged layers are reused across runs.

#### Scenario: Cache is read and written per service

- **WHEN** a service image is built
- **THEN** `cache-from` pulls the previously cached layers and `cache-to` writes updated layers back for reuse on subsequent runs

### Requirement: Docker workflow trigger coverage

The Docker workflow SHALL run on `push` to `main` and `develop` and on `pull_request` targeting `main`.

#### Scenario: Push to main builds images

- **WHEN** a commit is pushed to `main`
- **THEN** the Docker workflow is triggered and builds all service images in the matrix
