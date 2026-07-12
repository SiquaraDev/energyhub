# service-extraction Specification

## Purpose
TBD - created by archiving change implement-fase-15. Update Purpose after archive.
## Requirements
### Requirement: Each service is an independent deployable project

The system SHALL extract each target context (Auth, Clients, Contracts, Financial, Audit) into its own FastAPI project under `services/<name>-service/` with a dedicated `pyproject.toml`, application package, and dependency set, so it builds, runs, and versions independently of the others.

#### Scenario: Service builds and runs on its own

- **WHEN** a single extracted service directory is built and started in isolation
- **THEN** it starts successfully without importing code from any sibling service or from the monolith

#### Scenario: Auth service is extracted first

- **WHEN** the extraction order is applied
- **THEN** the Auth service — the only context with no upstream dependency — is extracted before the services that depend on it

### Requirement: Extracted code preserves the module's structure

The service extraction SHALL carry over the source module's entities, repositories, services, routers, DTOs, and mappers so the service exposes the same domain behavior it had inside the monolith.

#### Scenario: Domain layers move with the service

- **WHEN** an extracted service is inspected
- **THEN** its entities, repositories, application services, routers, DTOs, and mappers are present and correspond to those of the originating module

### Requirement: Each service owns its configuration and port

Each service SHALL expose configuration via a `Settings` object carrying at least its `app_name`, its listening `app_port`, and the discovery endpoint, with a distinct port assigned per service so services can run side by side.

#### Scenario: Configuration identifies the service uniquely

- **WHEN** a service loads its settings
- **THEN** the `app_name` matches the service and the `app_port` is unique across services (for example Auth on 8001, Clients on 8002, Contracts on 8003, Financial on 8004, Audit on 8005)

### Requirement: Each service owns its data store

Each extracted service SHALL own its own database or schema and MUST NOT reach directly into another service's tables; cross-context data is obtained through that context's service instead.

#### Scenario: No direct cross-service database access

- **WHEN** a service needs data owned by another context
- **THEN** it requests that data from the owning service rather than querying the other service's database directly

### Requirement: Each service is containerized with a health endpoint

Each service SHALL provide a `Dockerfile` producing a runnable image and expose a `/health` endpoint that reports the service is alive, so orchestration and discovery can probe it.

#### Scenario: Health endpoint responds when the service is up

- **WHEN** a running service receives a request on `/health`
- **THEN** it returns a successful response indicating the service is healthy

#### Scenario: Service image runs from its Dockerfile

- **WHEN** the service image is built from its `Dockerfile` and started
- **THEN** the containerized service serves requests on its configured port

