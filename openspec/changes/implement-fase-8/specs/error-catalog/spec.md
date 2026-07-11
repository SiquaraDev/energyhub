## ADDED Requirements

### Requirement: Exceptions carry error codes

Domain exceptions SHALL expose a stable `error_code` attribute (with a sensible default) in addition to their message, so failures can be identified by a machine-readable code.

#### Scenario: Exception exposes an error code

- **WHEN** a `ResourceNotFoundException` is constructed
- **THEN** it exposes an `error_code` (defaulting to `RESOURCE_NOT_FOUND`) alongside its message

### Requirement: Generic HTTP error catalog

The project MUST maintain `docs/API_ERRORS.md` documenting the common HTTP status codes the API returns (`400`, `401`, `403`, `404`, `409`, `422`, `500`), each with a description and its common causes.

#### Scenario: Common status codes are cataloged

- **WHEN** a consumer reads `docs/API_ERRORS.md`
- **THEN** each documented status code lists a description and the typical causes that trigger it

### Requirement: Module-specific error codes documented

`docs/API_ERRORS.md` SHALL enumerate module-specific error codes (for authentication, clients, contracts, and other modules) with a short explanation of each.

#### Scenario: Module error codes are listed

- **WHEN** a consumer looks up client errors in the catalog
- **THEN** codes such as `CLIENT_NOT_FOUND`, `INVALID_CNPJ`, and `CLIENT_ALREADY_EXISTS` are listed with descriptions
