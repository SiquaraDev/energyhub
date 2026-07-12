# integration-testing Specification

## Purpose
TBD - created by archiving change implement-fase-13. Update Purpose after archive.
## Requirements
### Requirement: Repository integration tests against a real database

The suite SHALL include repository integration tests that run against a real PostgreSQL instance provisioned by Testcontainers (`PostgresContainer`), verifying that entities persist and are read back through the repository.

#### Scenario: Save and find a client through the repository

- **WHEN** a `Client` is saved via `ClientRepository` against the Testcontainers PostgreSQL and then loaded by id
- **THEN** the loaded client is non-null and carries the same field values that were saved

#### Scenario: Custom finder resolves against the real schema

- **WHEN** a client is saved and `find_by_cnpj` is called with its CNPJ
- **THEN** the matching client is returned from the database

### Requirement: Container lifecycle scoped to the test module

Repository integration tests SHALL provision the database container and async engine once per test module and dispose of them afterward so the container is not recreated for every test.

#### Scenario: Container is reused within a module

- **WHEN** multiple tests in the same module run
- **THEN** they share a single module-scoped `PostgresContainer` and async engine that is disposed when the module finishes

### Requirement: API integration tests through the FastAPI app

The suite SHALL include API integration tests that exercise the running application via FastAPI's `TestClient`, authenticating first and then calling protected endpoints, asserting the HTTP status and response body.

#### Scenario: Authenticated request creates a client

- **WHEN** the test obtains a token via the login endpoint and POSTs a valid client payload to `/api/v1/clients` with an `Authorization: Bearer` header
- **THEN** the response status is `201` and the response body reflects the submitted client data

