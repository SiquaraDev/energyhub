## Context

Fase 3 produced the complete domain model (entities, value objects, enums, aggregates) but no persistence layer. The project runs PostgreSQL in Docker and has `alembic` declared in `pyproject.toml` (Fase 1). This phase builds the physical schema as a linear chain of Alembic migrations so the database can be created, evolved, and rolled back deterministically in every environment.

The schema must faithfully back the domain entities: auth (`users`, `roles`, `permissions`, `user_roles`, `role_permissions`), `clients`/`contacts`, `contracts`, negotiations (`negotiations`, `energy_transactions`), financial (`invoices`, `payments`), `audit_logs`, `notifications`, and `reports`. Alembic reads `settings.database_url` and `Base.metadata` so configuration stays single-sourced.

## Goals / Non-Goals

**Goals:**
- Configure Alembic driven by application settings and SQLAlchemy `Base.metadata`.
- Author versioned, individually reversible migrations that create every domain table with correct keys, constraints, and timestamp columns.
- Add performance indexes and data-integrity constraints (CHECK constraints + `updated_at` trigger).
- Seed baseline reference data (roles, permissions, ADMIN grants, default admin user) idempotently.
- Provide a validated upgrade/downgrade workflow.

**Non-Goals:**
- No SQLAlchemy ORM models / mappers (Fase 5 — Persistence).
- No repository or use-case implementations.
- No application-level data access or API endpoints.
- No autogenerate-driven migrations at this stage (schema is authored explicitly for control).

## Decisions

**Migration authoring — explicit `op` calls, not `--autogenerate`:**
- **Decision:** Hand-write migrations using `op.create_table`, `op.create_index`, and `op.execute` for raw SQL (triggers, checks, seeds).
- **Rationale:** ORM models do not exist yet (Fase 5), so `--autogenerate` has no metadata to diff. Explicit migrations give precise control over PostgreSQL-specific features (triggers, `gen_random_uuid()`, regex CHECKs).
- **Alternative considered:** Wait for ORM and autogenerate — rejected; it couples the schema milestone to Fase 5 and yields less control over Postgres-native constructs.

**Primary keys — UUID with `gen_random_uuid()` server default:**
- **Decision:** All entity tables use `UUID` PKs defaulting to `gen_random_uuid()`; join tables use composite PKs.
- **Rationale:** Matches the domain's UUID identity, avoids sequence contention, and keeps ID generation in the database.
- **Alternative considered:** Bigint identity columns — rejected; the domain models identity as UUID.

**Migration granularity — one migration per concern, chained linearly:**
- **Decision:** Split into ordered migrations: initial auth+clients+contracts tables, then remaining module tables, then indexes, then constraints/triggers, then seed data. Each sets `down_revision` to the prior revision.
- **Rationale:** Small, reviewable, independently reversible units with a clear history; mirrors the phase's step structure.
- **Alternative considered:** One monolithic migration — rejected; hard to review and to partially roll back.

**Timestamps + `updated_at` maintenance — DB trigger:**
- **Decision:** `created_at`/`updated_at` default to `CURRENT_TIMESTAMP`; a shared `update_updated_at_column()` trigger refreshes `updated_at` on UPDATE for every table that has it.
- **Rationale:** Guarantees the invariant regardless of the write path (app, migration, manual SQL).
- **Alternative considered:** Application-set timestamps — rejected as sole mechanism; not enforced at the DB and easy to bypass.

**Foreign-key delete behavior — CASCADE for owned children, RESTRICT (default) for references:**
- **Decision:** `contacts`→`clients`, `user_roles`/`role_permissions` links use `ON DELETE CASCADE`; `contracts`→`clients` keeps the default (restrict) to protect financial history.
- **Rationale:** Owned/child records should disappear with their parent; contracts are business records that must not vanish silently when a client row is removed.
- **Alternative considered:** CASCADE everywhere — rejected; risks silent loss of contractual/financial data.

**Seed data — idempotent, reversible migration with fixed UUIDs:**
- **Decision:** Insert roles/permissions/admin with hard-coded UUIDs; `downgrade` deletes exactly those rows.
- **Rationale:** Fixed IDs make grants and rollbacks deterministic and referenceable.
- **Alternative considered:** Seeding via an application script — rejected; loses versioning and reproducibility that migrations provide.

## Risks / Trade-offs

- **`gen_random_uuid()` unavailable** → On older PostgreSQL it lives in the `pgcrypto` extension; the first migration SHALL `CREATE EXTENSION IF NOT EXISTS pgcrypto` (no-op on PG13+ where it is built-in).
- **Seeded default admin is a security hole** → Ship with a clearly non-production bcrypt hash and document that the credential MUST be rotated before deployment; keep the seed reversible.
- **Migration ordering / FK dependency errors** → Author tables in dependency order (parents before children) and give every migration a symmetric, tested `downgrade`; validate with `upgrade head` then `downgrade base` in CI/local.
- **Drift once ORM lands in Fase 5** → Explicit schema may diverge from future ORM metadata; mitigate by treating these migrations as the source of truth and reconciling ORM models to them, not vice versa.
- **Regex CHECK constraints reject valid edge cases** (e.g., internationalized data) → Keep patterns conservative and align them with the domain value-object validation already defined in Fase 3.

## Migration Plan

1. Configure Alembic (`alembic.ini`, `env.py`) and confirm it connects using `settings.database_url`.
2. Apply migrations in order: schema tables → indexes → constraints/triggers → seed data via `alembic upgrade head`.
3. Verify with `alembic current` / `alembic history` and by inspecting tables and seeded rows.
4. Rollback strategy: each migration is reversible; use `alembic downgrade -1` (or `downgrade base` for a full teardown) to unwind, then `upgrade head` to restore.

## Open Questions

- Should composite/reporting indexes (e.g., `audit_logs.created_at`, `notifications.created_at`) be finalized now or deferred until query patterns from Fase 5+ are observed? (Current plan: create the obvious ones now, revisit under real workloads.)
- Final set of base permissions beyond the USER_* CRUD examples — to be expanded as module use cases are defined in later phases.
