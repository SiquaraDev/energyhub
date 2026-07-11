## ADDED Requirements

### Requirement: Versioned auth schema tables

Migrations SHALL create the authentication and authorization tables: `users`, `roles`, `permissions`, and the join tables `user_roles` and `role_permissions`.

#### Scenario: Auth entity tables created

- **WHEN** the schema migrations are applied to an empty database
- **THEN** `users`, `roles`, and `permissions` tables exist, each with a `UUID` primary key defaulting to `gen_random_uuid()` and `created_at`/`updated_at` timestamp columns

#### Scenario: Auth join tables created with composite keys

- **WHEN** the schema migrations are applied
- **THEN** `user_roles` and `role_permissions` exist with composite primary keys and foreign keys referencing their parent tables

### Requirement: Versioned business schema tables

Migrations SHALL create all business-domain tables: `clients`, `contacts`, `contracts`, `negotiations`, `energy_transactions`, `invoices`, `payments`, `audit_logs`, `notifications`, and `reports`.

#### Scenario: All domain tables present

- **WHEN** all schema migrations are applied
- **THEN** every table listed in the domain model exists with the columns, data types, and nullability defined for its entity

#### Scenario: Monetary and quantity columns use exact numeric types

- **WHEN** the `contracts` table is created
- **THEN** `energy_amount`, `unit_price`, and `total_value` use fixed-precision `Numeric` types rather than floating point

### Requirement: Keys, uniqueness, and referential integrity

Each table SHALL declare its primary key, applicable unique constraints, and foreign keys with delete behavior appropriate to the relationship (CASCADE for owned children, restrict for protected references).

#### Scenario: Unique business identifiers enforced

- **WHEN** a second `clients` row is inserted with an existing `cnpj`, or a `users` row with an existing `username` or `email`
- **THEN** the database rejects the insert due to a unique constraint violation

#### Scenario: Owned child rows cascade on parent delete

- **WHEN** a `clients` row is deleted
- **THEN** its dependent `contacts` rows are deleted via `ON DELETE CASCADE`

#### Scenario: Protected references block orphaning

- **WHEN** a `clients` row referenced by a `contracts` row is deleted
- **THEN** the delete is rejected to preserve contractual records

### Requirement: Reversible migrations

Every schema migration SHALL provide a `downgrade` that fully reverses its `upgrade`, dropping the objects it created in dependency-safe order.

#### Scenario: Full downgrade returns to empty schema

- **WHEN** a developer runs `alembic upgrade head` followed by `alembic downgrade base`
- **THEN** all domain tables and indexes created by these migrations are removed without foreign-key errors
