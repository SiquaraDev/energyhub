# api-usage-examples Specification

## Purpose
TBD - created by archiving change implement-fase-8. Update Purpose after archive.
## Requirements
### Requirement: Usage examples document

The project MUST provide `docs/API_EXAMPLES.md` containing runnable `curl` examples for the core API flows, including the authentication (login) flow and the primary client operations (create, list, get by id).

#### Scenario: Login example is documented

- **WHEN** a consumer reads the authentication section of `docs/API_EXAMPLES.md`
- **THEN** it shows a `curl` login request and a representative JSON response containing an access token

#### Scenario: Client operation examples are documented

- **WHEN** a consumer reads the clients section
- **THEN** it shows `curl` examples for creating, listing, and fetching a client

### Requirement: Examples show authenticated requests

Examples for protected endpoints SHALL show the `Authorization: Bearer <TOKEN>` header so consumers understand how to call secured operations.

#### Scenario: Protected request includes bearer token

- **WHEN** a consumer reads an example that calls a protected endpoint
- **THEN** the example includes an `Authorization: Bearer <TOKEN>` header

