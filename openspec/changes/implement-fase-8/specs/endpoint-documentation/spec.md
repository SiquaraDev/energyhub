## ADDED Requirements

### Requirement: Endpoint summaries and descriptions

Every API route SHALL be registered with a human-readable `summary` and `description` so each operation is self-explanatory in the generated documentation.

#### Scenario: Operation renders summary and description

- **WHEN** a route such as `POST /login` is added to a router
- **THEN** the generated operation carries the configured `summary` and `description` text

### Requirement: Documented response codes

Each route MUST document its possible responses per HTTP status code, associating each status with a description of the outcome.

#### Scenario: Success and error responses are listed

- **WHEN** a create-client route documents responses for `201`, `400`, and `409`
- **THEN** the operation's `responses` map lists each status code with its description in the OpenAPI schema

### Requirement: Endpoints grouped by tags

Routers MUST be included with OpenAPI tags (e.g. `Authentication`, `Clients`) so related operations are grouped in the documentation UI.

#### Scenario: Operations grouped under their tag

- **WHEN** the clients router is included with the `Clients` tag
- **THEN** its operations appear grouped under the `Clients` section in Swagger UI and ReDoc

### Requirement: Documented query parameters

Paginated and filtered list endpoints SHALL document their query parameters (e.g. `page`, `size`, `sort`, `direction`) with descriptions and validation bounds.

#### Scenario: Pagination parameters documented with bounds

- **WHEN** a list endpoint declares `page`, `size`, `sort`, and `direction` query parameters
- **THEN** each parameter is documented with its description and constraints (such as `size` bounded between 1 and 100)
