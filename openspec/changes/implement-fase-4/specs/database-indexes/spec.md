## ADDED Requirements

### Requirement: Single-column indexes on lookup fields

Migrations SHALL create indexes on columns frequently used in filters, joins, and lookups, including unique business identifiers and foreign keys.

#### Scenario: Lookup columns indexed

- **WHEN** the schema migrations are applied
- **THEN** indexes exist on `users.username`, `users.email`, `roles.name`, `permissions.name`, `clients.cnpj`, `clients.active`, `contacts.client_id`, `contacts.type`, `contracts.contract_number`, `contracts.client_id`, and `contracts.status`

### Requirement: Composite indexes for common query patterns

Migrations SHALL create composite indexes that match multi-column query and range patterns anticipated by the application.

#### Scenario: Date-range and multi-column indexes created

- **WHEN** the schema and index migrations are applied
- **THEN** a composite index exists on `contracts(start_date, end_date)` and on `contracts(client_id, status)`

#### Scenario: Time-ordered log indexes created

- **WHEN** the index migration is applied
- **THEN** indexes exist on `audit_logs.created_at` and `notifications.created_at` to support chronological queries

### Requirement: Indexes are reversible

Every index-creating migration SHALL drop the indexes it created in its `downgrade`.

#### Scenario: Index downgrade removes indexes

- **WHEN** the index migration is downgraded
- **THEN** all indexes it created are dropped and no orphaned index objects remain
