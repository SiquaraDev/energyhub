## ADDED Requirements

### Requirement: Shared base entity mapping

All persisted domain entities SHALL inherit from a shared `BaseEntity` that defines the primary key `id` and the `created_at`/`updated_at` timestamp columns, so identity and audit-timestamp columns are declared in exactly one place.

#### Scenario: Entity inherits identity and timestamps

- **WHEN** a domain entity is mapped
- **THEN** it exposes an `id` primary key and `created_at`/`updated_at` columns inherited from `BaseEntity` without redeclaring them

### Requirement: Domain entities mapped to their tables

The system SHALL map every domain entity — auth (`User`, `Role`, `Permission`), clients (`Client`, `Contact`), `Contract`, `Negotiation`, `EnergyTransaction`, `Invoice`, `Payment`, `AuditLog`, `Notification`, and `Report` — to its corresponding database table with correct column types, nullability, and unique constraints.

#### Scenario: Column types match the schema

- **WHEN** an entity with monetary or quantity fields is mapped (e.g. `Contract`, `Invoice`, `Payment`)
- **THEN** those fields use fixed-precision `Numeric` columns rather than floating-point types, matching the Fase 4 schema

#### Scenario: Table and column names align with migrations

- **WHEN** the ORM metadata is compared against the migrated schema
- **THEN** each mapped table name and its columns correspond to the tables created by the Fase 4 migrations

### Requirement: Entity relationships and indexes

Mapped entities SHALL declare their relationships (e.g. `User`↔`Role`, `Client`↔`Contact`, `Contract`→`Client`) and the indexes needed for their primary lookup paths.

#### Scenario: Relationship navigation is available

- **WHEN** a `Client` is loaded
- **THEN** its `contacts` relationship can be navigated, and a `User`'s `roles` relationship can be navigated

### Requirement: Mapping validated at startup

The ORM mapping SHALL be configured such that importing the application resolves all mappers without error, surfacing misconfigurations immediately.

#### Scenario: Application starts without mapping errors

- **WHEN** the application is started (e.g. `uvicorn energyhub.main:app`)
- **THEN** no SQLAlchemy mapper-configuration or relationship errors appear in the startup logs
