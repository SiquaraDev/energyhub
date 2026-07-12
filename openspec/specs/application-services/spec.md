# application-services Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Service per aggregate

The system SHALL provide an application service per aggregate (e.g. `UserService`, `ClientService`) in that module's `application/service/`, constructed with the repositories and mapper it needs, holding the business logic for creating, reading, updating, and deleting that aggregate.

#### Scenario: Service composed from its dependencies

- **WHEN** a service is instantiated
- **THEN** it receives its repositories and mapper as constructor dependencies and uses them for all persistence and translation

### Requirement: Create enforces uniqueness and domain rules

Service create operations SHALL verify uniqueness constraints and apply domain rules before persisting, returning the created entity as a response DTO.

#### Scenario: Create persists and returns a DTO

- **WHEN** `create` is called with a valid request DTO whose unique keys are not already used
- **THEN** the service maps the DTO to an entity, applies its rules (e.g. hashing a password, resolving role ids, assembling contacts), persists it, and returns the corresponding response DTO

#### Scenario: Create is blocked on duplicate

- **WHEN** `create` is called with a request DTO whose unique key already exists
- **THEN** the service raises the already-exists domain exception and persists nothing

### Requirement: Read, update, and delete honor existence

Service `find_by_id`, `update`, and `delete` operations SHALL confirm the target entity exists and raise a not-found domain exception when it does not.

#### Scenario: Find returns the mapped entity

- **WHEN** `find_by_id` is called with an existing id
- **THEN** the service returns the entity mapped to its response DTO

#### Scenario: Update refreshes and returns the entity

- **WHEN** `update` is called for an existing id with a valid request DTO
- **THEN** the service applies the changed fields, refreshes the update timestamp, persists, and returns the updated response DTO

#### Scenario: Delete removes an existing entity

- **WHEN** `delete` is called for an existing id
- **THEN** the service removes the entity; and **WHEN** the id does not exist, it raises a not-found domain exception

### Requirement: Paginated listing

Service listing operations SHALL accept a `PageRequest` and return a `PageResponse` of response DTOs so that list endpoints are bounded and carry page metadata.

#### Scenario: List returns a page of DTOs

- **WHEN** a service `find_all` is called with a `PageRequest`
- **THEN** it returns a `PageResponse` whose content is response DTOs and whose metadata reflects the requested page and total elements

