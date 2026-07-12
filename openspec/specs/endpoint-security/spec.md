# endpoint-security Specification

## Purpose
TBD - created by archiving change implement-fase-7. Update Purpose after archive.
## Requirements
### Requirement: Public authentication routes

The system SHALL register the authentication router under `/api/v1/auth` as a public route group that does not require a bearer token.

#### Scenario: Login is reachable without a token

- **WHEN** a client calls `POST /api/v1/auth/login` without an `Authorization` header
- **THEN** the request is accepted and processed by the authentication endpoint

### Requirement: Protected resource routes

The system SHALL protect the resource routers (clients, contracts, and other domain routers) with `get_current_user`, so every request to them requires a valid JWT.

#### Scenario: Protected route without a token

- **WHEN** a client calls a protected resource endpoint without a valid bearer token
- **THEN** the request is rejected with HTTP 401

#### Scenario: Protected route with a valid token

- **WHEN** a client calls a protected resource endpoint with a valid bearer token and sufficient grants
- **THEN** the request reaches the handler

### Requirement: Per-endpoint permission requirements

The system SHALL attach the appropriate `require_permission` guard to each resource operation, mapping CRUD actions to their permissions (e.g. `CLIENT_CREATE`, `CLIENT_READ`, `CLIENT_UPDATE`, `CLIENT_DELETE`).

#### Scenario: Create requires the create permission

- **WHEN** a client with a valid token but without `CLIENT_CREATE` calls the create-client endpoint
- **THEN** the request is rejected with HTTP 403

#### Scenario: Read requires the read permission

- **WHEN** a client with a valid token and `CLIENT_READ` calls the list-clients endpoint
- **THEN** the request is authorized and the handler runs

### Requirement: CORS configuration

The system SHALL register CORS middleware on the FastAPI application so browser clients from the configured origins can call the API.

#### Scenario: Cross-origin request is permitted

- **WHEN** a browser client from an allowed origin sends a request with a CORS preflight
- **THEN** the middleware responds with the appropriate CORS headers allowing the call

