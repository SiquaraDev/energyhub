## MODIFIED Requirements

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
