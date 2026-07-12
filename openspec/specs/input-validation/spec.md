# input-validation Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Reusable custom validators

The system SHALL provide reusable custom validators (e.g. `CnpjValidator`) in `shared/application/validation/` that encapsulate cross-cutting input rules as standalone, independently testable functions rather than being duplicated inside each DTO.

#### Scenario: Validator accepts a valid value

- **WHEN** a custom validator is invoked with a value that satisfies its rule (e.g. a well-formed CNPJ)
- **THEN** the validator returns the value unchanged

#### Scenario: Validator rejects an invalid value

- **WHEN** a custom validator is invoked with a value that violates its rule (e.g. a malformed CNPJ)
- **THEN** the validator raises a validation error identifying the offending field

### Requirement: Validators applied to DTOs

Request DTOs SHALL apply the relevant custom validators through Pydantic `@field_validator` methods so that invalid input is rejected at DTO construction, before any service or repository is reached.

#### Scenario: Invalid field rejected at the boundary

- **WHEN** a request DTO carrying a field guarded by a custom validator is constructed with an invalid value
- **THEN** DTO construction fails with a validation error and no service logic is executed

#### Scenario: Non-empty string enforcement

- **WHEN** a request DTO field requiring a non-empty value (e.g. `username`, contact `name`) receives an empty or whitespace-only string
- **THEN** the field validator raises an error indicating the value cannot be empty

