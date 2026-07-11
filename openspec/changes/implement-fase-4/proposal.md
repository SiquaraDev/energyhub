## Why

The EnergyHub domain model (Fase 3) defines all business entities, but there is no physical database to persist them. This phase creates the complete PostgreSQL schema in a fully versioned, reproducible way using Alembic migrations, so the database structure evolves under source control and can be applied identically across every environment.

## What Changes

- Add and configure Alembic in the project (`alembic.ini`, `alembic/env.py`) wired to `settings.database_url` and `Base.metadata`, using a UTC, timestamped migration file naming convention.
- Create versioned migrations that build every table for the domain model: `users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `clients`, `contacts`, `contracts`, `negotiations`, `energy_transactions`, `invoices`, `payments`, `audit_logs`, `notifications`, `reports`.
- Define primary keys (UUID with `gen_random_uuid()`), foreign keys with appropriate `ON DELETE` behavior, unique constraints, and `created_at`/`updated_at` timestamp columns.
- Create single-column and composite indexes to optimize the most frequent query paths.
- Add CHECK constraints (email/CNPJ format, positive monetary values, contract date ordering) and an `updated_at` auto-update trigger applied to every table that has the column.
- Seed initial data: default roles (ADMIN, OPERATOR, CLIENT), base permissions, role-permission grants for ADMIN, and a default admin user.
- Establish and validate the migration workflow (`upgrade head`, `current`, `history`, and reversible `downgrade`).

## Capabilities

### New Capabilities

- `alembic-configuration`: Alembic installed and configured against the project settings and SQLAlchemy `Base.metadata`, with UTC timestamped migration naming and online/offline migration support.
- `database-schema-migrations`: Versioned migrations that create all domain tables with columns, primary keys, foreign keys, unique constraints, and timestamp columns, each with a correct reversible `downgrade`.
- `database-indexes`: Single-column and composite indexes on high-frequency query columns to optimize read performance.
- `database-constraints`: CHECK constraints for data integrity and an `updated_at` trigger function applied across tables.
- `database-seed-data`: Idempotent seed migration inserting default roles, permissions, ADMIN grants, and the default admin user.

### Modified Capabilities

None — this phase introduces the persistence schema; it does not change existing spec-level behavior.

## Impact

- **Dependencies**: Adds `alembic` (already declared in `pyproject.toml` from Fase 1). Requires a running PostgreSQL instance (Docker) and the `pgcrypto`/built-in `gen_random_uuid()` capability.
- **New artifacts**: `alembic/` directory (env, script templates, `versions/`) and `alembic.ini` at the project root.
- **Consumes**: `energyhub.config.settings.database_url` and `energyhub.shared.infrastructure.persistence.database.Base` (established in earlier phases).
- **Enables**: Fase 5 (Persistence) — repository and ORM implementations require this schema to exist.
- **Data**: Introduces seed data including a default admin account; credentials must be rotated before any production use.
