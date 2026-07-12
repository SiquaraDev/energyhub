# application-container-image Specification

## Purpose
TBD - created by archiving change implement-fase-14. Update Purpose after archive.
## Requirements
### Requirement: Multi-stage build image

The system SHALL provide a `Dockerfile` that uses a multi-stage build: a build stage that installs Poetry and resolves production-only dependencies, and a separate runtime stage based on `python:3.12-slim` that copies only the installed dependencies and application code.

#### Scenario: Image builds successfully

- **WHEN** `docker build -t energyhub:latest .` is run from the project root
- **THEN** the build completes without error and produces the `energyhub:latest` image

#### Scenario: Runtime stage excludes build tooling

- **WHEN** the runtime stage is assembled from the build stage
- **THEN** only the resolved site-packages and application code are copied in, and build-only tooling (compilers, Poetry cache) is not present in the final image

### Requirement: Non-root runtime user

The image SHALL create and run as a dedicated non-root user (`appuser`), and the application files SHALL be owned by that user.

#### Scenario: Container process runs as non-root

- **WHEN** a container is started from the image
- **THEN** the application process runs as `appuser` rather than `root`

### Requirement: Application entrypoint and exposed port

The image SHALL expose port `8000` and its default command SHALL start the API via `uvicorn energyhub.main:app` bound to `0.0.0.0:8000`.

#### Scenario: Container serves the API

- **WHEN** the container is run with port `8000` published
- **THEN** the API is reachable on the published port and responds to requests

### Requirement: Minimal build context

The system SHALL provide a `.dockerignore` that excludes version-control, virtual-environment, cache, test-artifact, and local-environment files from the build context.

#### Scenario: Excluded paths are not sent to the build

- **WHEN** the image is built
- **THEN** paths such as `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, and `.env` are excluded from the build context and do not appear in the image

