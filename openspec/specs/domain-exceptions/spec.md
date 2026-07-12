# domain-exceptions Specification

## Purpose
TBD - created by archiving change implement-fase-6. Update Purpose after archive.
## Requirements
### Requirement: Domain exception hierarchy per module

The system SHALL define domain-specific exceptions per module in that module's `domain/exception/` covering not-found, already-exists, and invalid-state conditions (e.g. `UserAlreadyExistsException`, `InvalidCredentialsException`, `ClientNotFoundException`, `InvalidCnpjException`, `InvalidContractStatusException`), layered on the shared `ResourceNotFoundException` and `ValidationException`.

#### Scenario: Domain exceptions extend shared base exceptions

- **WHEN** a module defines a domain exception for a business-rule violation
- **THEN** it extends the appropriate shared base exception so that generic handlers can catch it by base type

### Requirement: Services raise domain exceptions on rule violations

Application services SHALL raise the relevant domain exception when a business rule is violated, rather than returning null, sentinel values, or leaking raw persistence errors.

#### Scenario: Duplicate creation raises already-exists

- **WHEN** a create operation is attempted for an entity whose unique key already exists (e.g. an existing username, email, or CNPJ)
- **THEN** the service raises the corresponding already-exists domain exception and does not persist a duplicate

#### Scenario: Missing entity raises not-found

- **WHEN** a find, update, or delete operation targets an id that does not exist
- **THEN** the service raises a not-found domain exception carrying a descriptive message

