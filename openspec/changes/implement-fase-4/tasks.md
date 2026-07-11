## 1. Alembic Configuration

- [ ] 1.1 Ensure `alembic` is declared in `pyproject.toml` and install it (`poetry add alembic` if missing)
- [ ] 1.2 Initialize the Alembic environment with `poetry run alembic init alembic`
- [ ] 1.3 Configure `alembic.ini`: set `script_location = alembic`, UTC `timezone`, and a timestamped `file_template`
- [ ] 1.4 Edit `alembic/env.py` to import `settings` and set `sqlalchemy.url` from `settings.database_url`
- [ ] 1.5 Set `target_metadata = Base.metadata` in `alembic/env.py` (import `Base` from the persistence module)
- [ ] 1.6 Implement `run_migrations_offline()` with literal binds and `run_migrations_online()` with a NullPool connection
- [ ] 1.7 Verify configuration with `poetry run alembic current` (connects without error)

## 2. Initial Schema Migration (auth, clients, contracts)

- [ ] 2.1 Create the initial migration: `poetry run alembic revision -m "initial schema"`
- [ ] 2.2 Add `CREATE EXTENSION IF NOT EXISTS pgcrypto` at the top of the initial `upgrade` to guarantee `gen_random_uuid()`
- [ ] 2.3 Create `users` table (UUID PK, username/password/email/full_name/active, timestamps, unique username+email)
- [ ] 2.4 Create `roles` and `permissions` tables (UUID PK, name unique, description, timestamps)
- [ ] 2.5 Create `user_roles` and `role_permissions` join tables (composite PKs, FKs with `ON DELETE CASCADE`)
- [ ] 2.6 Create `clients` table (UUID PK, cnpj unique, corporate/trade name, contact fields, active, timestamps)
- [ ] 2.7 Create `contacts` table (UUID PK, `client_id` FK `ON DELETE CASCADE`, name/email/phone/position/type, timestamps)
- [ ] 2.8 Create `contracts` table (UUID PK, contract_number unique, `client_id` FK restrict, dates, Numeric amounts, status/type, timestamps)
- [ ] 2.9 Write a symmetric `downgrade` that drops the above tables and their indexes in reverse dependency order

## 3. Remaining Domain Table Migrations

- [ ] 3.1 Create migration for `negotiations` and `energy_transactions` tables with their FKs and timestamps
- [ ] 3.2 Create migration for `invoices` and `payments` tables with their FKs, Numeric monetary columns, and timestamps
- [ ] 3.3 Create migration for `audit_logs` table with its columns and timestamps
- [ ] 3.4 Create migration for `notifications` and `reports` tables with their columns and timestamps
- [ ] 3.5 Chain each migration's `down_revision` to the prior revision and provide reversible `downgrade`s

## 4. Indexes

- [ ] 4.1 Confirm single-column indexes on lookup/FK columns are created inline with their table migrations (users, roles, permissions, clients, contacts, contracts)
- [ ] 4.2 Create an "additional indexes" migration: `poetry run alembic revision -m "create additional indexes"`
- [ ] 4.3 Add composite indexes: `contracts(client_id, status)` and `contracts(start_date, end_date)`
- [ ] 4.4 Add time-ordered indexes: `audit_logs.created_at` and `notifications.created_at`
- [ ] 4.5 Write the `downgrade` dropping every index created in this migration

## 5. Constraints and Triggers

- [ ] 5.1 Create a constraints migration: `poetry run alembic revision -m "create constraints"`
- [ ] 5.2 Add CHECK constraint on `users.email` for valid email format
- [ ] 5.3 Add CHECK constraint on `clients.cnpj` for formatted or 14-digit CNPJ
- [ ] 5.4 Add CHECK constraints on `contracts`: `end_date > start_date` and positive `energy_amount`/`unit_price`/`total_value`
- [ ] 5.5 Create the shared `update_updated_at_column()` trigger function
- [ ] 5.6 Attach an `update_<table>_updated_at` trigger to every table that has an `updated_at` column
- [ ] 5.7 Write the `downgrade` dropping triggers, the function, and all CHECK constraints

## 6. Seed Data

- [ ] 6.1 Create a seed migration: `poetry run alembic revision -m "insert initial data"`
- [ ] 6.2 Insert default roles `ADMIN`, `OPERATOR`, `CLIENT` with fixed UUIDs
- [ ] 6.3 Insert base permissions (USER_CREATE/READ/UPDATE/DELETE, extend as needed) with fixed UUIDs
- [ ] 6.4 Grant every seeded permission to the `ADMIN` role in `role_permissions`
- [ ] 6.5 Insert the default `admin` user with a bcrypt password hash and link it to the `ADMIN` role via `user_roles`
- [ ] 6.6 Write the `downgrade` that deletes exactly the seeded user, grants, permissions, and roles

## 7. Validation

- [ ] 7.1 Run `poetry run alembic upgrade head` against the Dockerized PostgreSQL and confirm success
- [ ] 7.2 Verify migration state with `poetry run alembic current` and `poetry run alembic history`
- [ ] 7.3 Connect to the database and confirm all tables exist (`\dt`) and seed rows are present (`roles`, `permissions`, `users`)
- [ ] 7.4 Confirm `alembic_version` reflects the latest head revision
- [ ] 7.5 Test reversibility: `poetry run alembic downgrade base` then `poetry run alembic upgrade head` complete without errors
- [ ] 7.6 Run `openspec validate implement-fase-4` and confirm the change is valid
