# rest-api-endpoints Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Router per module

The system SHALL provide a REST router per module (e.g. `UserRouter`, `ClientRouter`) in that module's `presentation/router/`, extending the shared `BaseRouter`, that registers the module's endpoints and delegates each to a service or use case.

#### Scenario: Router registers CRUD endpoints

- **WHEN** a router is initialized with its service dependency
- **THEN** it registers create (POST), read-by-id (GET), update (PUT), and delete (DELETE) routes bound to the corresponding service operations

### Requirement: Endpoints exchange DTOs

Endpoints SHALL accept request DTOs as input and return response DTOs as output, delegating all logic to the service/use-case layer and performing no business logic in the router.

#### Scenario: Create endpoint returns a response DTO

- **WHEN** the create endpoint receives a valid request DTO
- **THEN** it delegates to the service and returns the resulting response DTO with a created status

#### Scenario: Read endpoint returns the entity DTO

- **WHEN** the read-by-id endpoint is called with an existing id
- **THEN** it returns the corresponding response DTO

### Requirement: Paginated list endpoints

List endpoints SHALL accept pagination query parameters (`page`, `size`, optional `sort`, `direction`) with bounded, validated ranges and return a `PageResponse` of response DTOs.

#### Scenario: List endpoint bounds page size

- **WHEN** the list endpoint is called with pagination query parameters
- **THEN** the parameters are validated against their allowed ranges and a `PageResponse` of response DTOs is returned

### Requirement: OpenAPI documentation

The API SHALL be self-documented through FastAPI's generated OpenAPI schema — with configured API title, description, and version, and per-endpoint/per-field descriptions — served at `/docs` and `/redoc`.

#### Scenario: Interactive docs are served

- **WHEN** the application is running and `/docs` is requested
- **THEN** an OpenAPI/Swagger page is served listing the registered endpoints with their request/response schemas

#### Scenario: API metadata is configured

- **WHEN** the OpenAPI schema is generated
- **THEN** it carries the configured API title, description, and version

