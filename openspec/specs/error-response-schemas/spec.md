# error-response-schemas Specification

## Purpose
TBD - created by archiving change implement-fase-8. Update Purpose after archive.
## Requirements
### Requirement: Standard error response model

The system SHALL provide an `ErrorResponse` model in `shared/presentation/response/` carrying `timestamp`, `status`, `error`, `message`, and `path` fields, each documented with a description and example.

#### Scenario: Error response captures request context

- **WHEN** an `ErrorResponse` is produced for a failed request
- **THEN** it includes the HTTP status, an error type, a human-readable message, and the request path that caused the error

### Requirement: Validation error response model

The system SHALL provide a `ValidationErrorResponse` model composed of `status`, `message`, and a list of `FieldError` entries (each with `field` and `message`) so validation failures report every offending field.

#### Scenario: Validation failure lists field errors

- **WHEN** a request fails schema validation on multiple fields
- **THEN** the response body contains a `ValidationErrorResponse` whose `errors` list has one `FieldError` per invalid field

### Requirement: Handlers emit documented error bodies

Global exception handlers MUST return the standardized error models so that runtime error responses match the documented schemas.

#### Scenario: Not-found exception returns ErrorResponse

- **WHEN** a `ResourceNotFoundException` propagates to the handler
- **THEN** the response has status `404` and a body conforming to `ErrorResponse`

#### Scenario: Request validation returns ValidationErrorResponse

- **WHEN** a `RequestValidationError` is raised for an invalid request
- **THEN** the response has status `400` and a body conforming to `ValidationErrorResponse`

