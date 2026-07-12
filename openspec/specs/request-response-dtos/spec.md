# request-response-dtos Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Request DTOs per entity

The system SHALL provide a Pydantic request DTO for every write-facing entity (e.g. `UserRequestDTO`, `ClientRequestDTO`, `ContactRequestDTO`, `ContractRequestDTO`, and the remaining modules) in that module's `application/dto/`, declaring the fields accepted from clients with their type, required/optional status, and field constraints.

#### Scenario: Valid payload is accepted

- **WHEN** a request DTO is instantiated from a payload that satisfies every declared field constraint
- **THEN** a validated DTO instance is produced carrying the typed field values

#### Scenario: Constraint violation is rejected

- **WHEN** a request DTO is instantiated from a payload violating a declared constraint (e.g. `username` shorter than `min_length`, missing required field, or malformed email)
- **THEN** a Pydantic validation error is raised and no DTO instance is produced

### Requirement: Response DTOs per entity

The system SHALL provide a Pydantic response DTO for every read-facing entity (e.g. `UserResponseDTO`, `RoleResponseDTO`, `PermissionResponseDTO`, `ClientResponseDTO`, `ContactResponseDTO`, …) extending the shared `BaseDTO`, exposing the entity's audit fields (`id`, `created_at`, `updated_at`) plus its domain fields and nested response DTOs for related entities.

#### Scenario: Response DTO carries audit and domain fields

- **WHEN** a response DTO is constructed for a persisted entity
- **THEN** it exposes the entity `id`, `created_at`, and `updated_at` inherited from `BaseDTO` together with the entity's domain fields

#### Scenario: Nested relations are represented as response DTOs

- **WHEN** a response DTO represents an entity that owns related entities (e.g. a user with roles, a client with contacts)
- **THEN** the related entities are exposed as a list of their own response DTOs rather than raw entities

### Requirement: DTOs expose OpenAPI schema metadata

Request and response DTOs SHALL declare descriptive metadata (field descriptions and constraints via `Field(...)`) so that the generated OpenAPI schema documents each field.

#### Scenario: Field descriptions surface in the schema

- **WHEN** the OpenAPI schema is generated from a DTO whose fields carry `description` metadata
- **THEN** each field's description and constraints appear in the schema for that model

