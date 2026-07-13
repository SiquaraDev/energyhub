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

The seed migration SHALL insert a default admin user assigned the `ADMIN` role, and its bcrypt-hashed password MUST be derived from a deploy-time secret rather than a committed known hash of a published password. Outside local development, the admin account MUST require its password to be rotated on first use.

#### Scenario: Admin user created and linked

- **WHEN** the seed migration is applied
- **THEN** a `users` row with username `admin`, an active flag set true, and a bcrypt password hash exists, and `user_roles` links it to the `ADMIN` role

#### Scenario: Admin password comes from a deploy-time secret

- **WHEN** the seed migration runs
- **THEN** the admin password hash is derived from a deploy-time secret and no committed known password hash is used

#### Scenario: Admin must rotate on first use outside local development

- **WHEN** the admin account is provisioned in a non-local profile
- **THEN** it is flagged to require a password rotation on first use so the bootstrap credential does not persist

### Requirement: Seed migration is idempotent and reversible

The seed migration SHALL be safely re-applicable and SHALL provide a `downgrade` that removes exactly the rows it inserted.

#### Scenario: Seed downgrade removes seeded rows

- **WHEN** the seed migration is downgraded
- **THEN** the seeded admin user, ADMIN permission grants, permissions, and roles inserted by the migration are deleted, leaving no residual seed rows

