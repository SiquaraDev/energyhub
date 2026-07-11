## ADDED Requirements

### Requirement: Role query service

The system SHALL provide a `RoleService` in `auth/application/service/` that exposes `find_all` and `find_by_name` over the roles seeded in Fase 4, returning `RoleResponseDTO` values.

#### Scenario: Listing all roles

- **WHEN** `find_all` is called
- **THEN** every role (e.g. `ADMIN`, `OPERATOR`, `CLIENT`) is returned as a `RoleResponseDTO`

#### Scenario: Looking up a role by name

- **WHEN** `find_by_name` is called with an existing role name
- **THEN** the matching `RoleResponseDTO` is returned

#### Scenario: Unknown role name

- **WHEN** `find_by_name` is called with a name that does not exist
- **THEN** a resource-not-found error is raised

### Requirement: Permission query service

The system SHALL provide a `PermissionService` in `auth/application/service/` that exposes `find_all` and `find_by_role_name`, returning `PermissionResponseDTO` values.

#### Scenario: Listing all permissions

- **WHEN** `find_all` is called
- **THEN** every permission is returned as a `PermissionResponseDTO`

#### Scenario: Permissions scoped to a role

- **WHEN** `find_by_role_name` is called with a role name
- **THEN** only the permissions granted to that role are returned
