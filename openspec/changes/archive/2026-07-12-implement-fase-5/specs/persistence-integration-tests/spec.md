## ADDED Requirements

### Requirement: Async test session fixture

The test suite SHALL provide an async database session fixture that yields an `AsyncSession` against a test database and isolates each test (e.g. rollback or truncate between tests) so tests do not leak state.

#### Scenario: Tests receive an isolated session

- **WHEN** an async persistence test requests the session fixture
- **THEN** it receives a working `AsyncSession`, and changes made by one test are not visible to another

### Requirement: CRUD persistence tests

The suite SHALL include integration tests that save an entity through a repository and read it back, verifying that generated identity and persisted fields are correct.

#### Scenario: Save then read back a client

- **WHEN** a `Client` is saved via `ClientRepository` and then loaded
- **THEN** the loaded client has a non-null `id` and the same field values that were saved

### Requirement: Finder, filter, and pagination tests

The suite SHALL include tests exercising custom finder methods, filter-based queries, and paginated listing to confirm they return the expected rows.

#### Scenario: Custom finder returns the saved row

- **WHEN** a client is saved and then `find_by_cnpj` is called with its CNPJ
- **THEN** the matching client is returned with the expected fields

#### Scenario: Pagination and filtering return bounded, correct results

- **WHEN** more rows than one page exist and a paginated, filtered query is executed
- **THEN** the returned page respects the page size and the total count reflects all matching rows
