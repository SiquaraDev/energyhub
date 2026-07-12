# schema-documentation Specification

## Purpose
TBD - created by archiving change implement-fase-8. Update Purpose after archive.
## Requirements
### Requirement: Documented DTO fields

Request and response Pydantic DTOs SHALL annotate their fields with `Field(description=...)` so every schema property renders a human-readable description in the documentation.

#### Scenario: DTO field renders its description

- **WHEN** a DTO field such as `username` is defined with a `Field` description
- **THEN** the generated schema for that DTO includes the description on the corresponding property

### Requirement: Field-level examples

DTO fields MUST provide representative examples via `Field(example=...)` so the documentation and Swagger UI show example request/response payloads.

#### Scenario: Example payload rendered in docs

- **WHEN** a DTO's fields declare examples
- **THEN** Swagger UI presents an example request body assembled from those field examples

### Requirement: Documented field constraints

DTO fields SHALL declare their validation constraints (such as `min_length`, `max_length`, and typed fields like `EmailStr`) so the constraints appear in the schema and are enforced at request time.

#### Scenario: Constraints surface in the schema

- **WHEN** a field declares `min_length=3` and `max_length=50`
- **THEN** the generated schema documents those bounds and a request violating them is rejected as invalid input

