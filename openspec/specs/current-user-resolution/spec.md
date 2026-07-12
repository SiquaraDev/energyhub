# current-user-resolution Specification

## Purpose
TBD - created by archiving change implement-fase-7. Update Purpose after archive.
## Requirements
### Requirement: Bearer token resolves to the current user

The system SHALL provide a `get_current_user` FastAPI dependency that reads the `Authorization: Bearer` credentials, extracts the username via `JwtService`, loads the user, and returns a `UserDetails` instance.

#### Scenario: Valid token resolves a user

- **WHEN** a request carries a valid bearer token for an existing user
- **THEN** `get_current_user` returns a `UserDetails` wrapping that user

#### Scenario: Missing or invalid token is rejected

- **WHEN** a request has no bearer token or a token whose subject cannot be extracted
- **THEN** `get_current_user` raises HTTP 401 with a `WWW-Authenticate: Bearer` header

#### Scenario: Token subject does not match any user

- **WHEN** a valid token's subject does not correspond to any stored user
- **THEN** `get_current_user` raises HTTP 401

### Requirement: UserDetails exposes identity and grants

`UserDetails` SHALL wrap a `User` and expose `username`, `active`, `roles` (role names), and `permissions` (the flattened permission names across the user's roles).

#### Scenario: Permissions are flattened across roles

- **WHEN** `permissions` is read on a `UserDetails` whose user has multiple roles
- **THEN** it returns the combined list of permission names from every role

#### Scenario: Roles are exposed by name

- **WHEN** `roles` is read on a `UserDetails`
- **THEN** it returns the names of the roles assigned to the user

