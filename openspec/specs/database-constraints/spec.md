# database-constraints Specification

## Purpose
TBD - created by archiving change implement-fase-4. Update Purpose after archive.
## Requirements
### Requirement: Data-integrity CHECK constraints

Migrations SHALL add CHECK constraints that enforce domain invariants at the database level, consistent with the value-object validations defined in the domain model.

#### Scenario: Email format enforced

- **WHEN** a `users` row is inserted with a value that does not match a valid email pattern
- **THEN** the database rejects the insert due to the email CHECK constraint

#### Scenario: CNPJ format enforced

- **WHEN** a `clients` row is inserted with a `cnpj` that matches neither the formatted nor the 14-digit pattern
- **THEN** the database rejects the insert due to the CNPJ CHECK constraint

#### Scenario: Contract date ordering enforced

- **WHEN** a `contracts` row is inserted with `end_date` not later than `start_date`
- **THEN** the database rejects the insert due to the date CHECK constraint

#### Scenario: Positive monetary values enforced

- **WHEN** a `contracts` row is inserted with a non-positive `energy_amount`, `unit_price`, or `total_value`
- **THEN** the database rejects the insert due to the positive-values CHECK constraint

### Requirement: Automatic `updated_at` maintenance

A shared trigger function SHALL update the `updated_at` column to the current timestamp on every row update, and it SHALL be applied to every table that has an `updated_at` column.

#### Scenario: updated_at refreshes on update

- **WHEN** an existing row in a table with `updated_at` is updated
- **THEN** its `updated_at` value is set to the current timestamp by the trigger, independent of the value supplied by the caller

#### Scenario: Trigger applied across all timestamped tables

- **WHEN** the constraints migration is applied
- **THEN** an `update_updated_at` trigger backed by a single shared function exists on each table that has an `updated_at` column

### Requirement: Constraints and triggers are reversible

The constraints migration SHALL drop all CHECK constraints, triggers, and the trigger function it created in its `downgrade`.

#### Scenario: Constraint downgrade cleans up

- **WHEN** the constraints migration is downgraded
- **THEN** the CHECK constraints, `updated_at` triggers, and the shared trigger function are removed

