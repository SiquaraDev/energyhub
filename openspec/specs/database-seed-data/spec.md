# database-seed-data Specification

## Purpose
TBD - created by archiving change implement-fase-4. Update Purpose after archive.
## Requirements
### Requirement: Seed default roles and permissions

A seed migration SHALL insert the baseline roles (`ADMIN`, `OPERATOR`, `CLIENT`) and the base permissions using fixed, deterministic UUIDs.

#### Scenario: Default roles present after seed

- **WHEN** the seed migration is applied
- **THEN** rows for roles `ADMIN`, `OPERATOR`, and `CLIENT` exist with their predefined UUIDs

#### Scenario: Base permissions present after seed

- **WHEN** the seed migration is applied
- **THEN** the base permission rows exist with their predefined UUIDs and descriptions

### Requirement: Grant all permissions to ADMIN

The seed migration SHALL associate every seeded permission with the `ADMIN` role.

#### Scenario: ADMIN has all permissions

- **WHEN** the seed migration is applied
- **THEN** `role_permissions` contains one row linking the `ADMIN` role to each seeded permission

### Requirement: Seed default admin user

The seed migration SHALL insert a default admin user with a bcrypt-hashed password and assign it the `ADMIN` role.

#### Scenario: Admin user created and linked

- **WHEN** the seed migration is applied
- **THEN** a `users` row with username `admin`, an active flag set true, and a bcrypt password hash exists, and `user_roles` links it to the `ADMIN` role

### Requirement: Seed migration is idempotent and reversible

The seed migration SHALL be safely re-applicable and SHALL provide a `downgrade` that removes exactly the rows it inserted.

#### Scenario: Seed downgrade removes seeded rows

- **WHEN** the seed migration is downgraded
- **THEN** the seeded admin user, ADMIN permission grants, permissions, and roles inserted by the migration are deleted, leaving no residual seed rows

