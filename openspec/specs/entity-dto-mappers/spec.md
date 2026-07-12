# entity-dto-mappers Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Mapper per module

The system SHALL provide a mapper class per module (e.g. `UserMapper`, `ClientMapper`) in that module's `application/mapper/` that converts between domain entities and DTOs, so no service, router, or repository performs entity-to-DTO translation inline.

#### Scenario: Mapper is the single translation point

- **WHEN** an entity must be exposed as a DTO or a request DTO must become an entity
- **THEN** the conversion is performed through the module mapper rather than by ad-hoc field copying elsewhere

### Requirement: Request DTO to entity conversion

Mappers SHALL expose a `to_entity` operation that builds a new domain entity from a request DTO, populating the entity's writable fields and leaving generated fields (id, timestamps) to be assigned by persistence.

#### Scenario: Entity built from request DTO

- **WHEN** `to_entity` is called with a valid request DTO
- **THEN** a domain entity is returned with its writable fields populated from the DTO's values

### Requirement: Entity to response DTO conversion

Mappers SHALL expose a `to_response_dto` operation that builds a response DTO from a domain entity, including the entity's audit fields and mapping any related entities into their nested response DTOs.

#### Scenario: Response DTO built from entity

- **WHEN** `to_response_dto` is called with a persisted entity
- **THEN** a response DTO is returned carrying the entity's `id`, timestamps, and domain fields

#### Scenario: Related entities mapped recursively

- **WHEN** `to_response_dto` is called for an entity holding related entities (e.g. a user's roles and their permissions)
- **THEN** each related entity is converted to its own response DTO and attached to the parent response DTO

