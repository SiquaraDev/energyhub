## ADDED Requirements

### Requirement: Generic async repository base

The system SHALL provide a generic `SQLAlchemyRepository[T, ID]` base class that is constructed with an `AsyncSession` and the mapped entity type, and that all concrete repositories extend.

#### Scenario: Repository is bound to a session and entity type

- **WHEN** a concrete repository extends `SQLAlchemyRepository[T, ID]` and is instantiated with a session
- **THEN** it inherits the standard operations bound to that session and entity type without redefining them

### Requirement: Standard CRUD operations

The generic repository SHALL expose async operations to persist and retrieve entities: `save`, `find_by_id`, `find_all`, `delete`, and `exists_by_id`.

#### Scenario: Save persists a new entity

- **WHEN** `save` is called with a new entity
- **THEN** the entity is added and flushed so its generated `id` is populated, and the persisted entity is returned

#### Scenario: Find by id returns the matching entity or none

- **WHEN** `find_by_id` is called with an existing id
- **THEN** the corresponding entity is returned; and **WHEN** called with an unknown id, `None` is returned

#### Scenario: Delete removes the entity

- **WHEN** `delete` is called for an existing entity
- **THEN** the entity is removed and a subsequent `find_by_id` for that id returns `None`

#### Scenario: Existence check

- **WHEN** `exists_by_id` is called
- **THEN** it returns `True` if a row with that id exists and `False` otherwise
