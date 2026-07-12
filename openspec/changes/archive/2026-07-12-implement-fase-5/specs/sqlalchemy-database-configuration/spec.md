## ADDED Requirements

### Requirement: Async engine bound to application settings

The system SHALL create a single async SQLAlchemy engine using `settings.database_url`, and its SQL echoing SHALL follow `settings.debug`. The engine SHALL use the asyncpg driver.

#### Scenario: Engine reads configuration from settings

- **WHEN** the persistence module is imported
- **THEN** the async engine is created from `settings.database_url` with `echo` set to `settings.debug`, and no hard-coded connection string is present

#### Scenario: Engine uses the async driver

- **WHEN** the engine issues a query
- **THEN** it does so over an async connection (asyncpg) without blocking the event loop

### Requirement: Declarative base for ORM models

The system SHALL expose a single `Base` class derived from SQLAlchemy `DeclarativeBase` that all mapped entities inherit from, so that `Base.metadata` describes the full ORM schema.

#### Scenario: Base is the shared metadata root

- **WHEN** any mapped entity is defined
- **THEN** it inherits from the shared `Base` and its table is registered under `Base.metadata`

### Requirement: Async session factory and dependency

The system SHALL provide an `async_sessionmaker` producing `AsyncSession` instances with `expire_on_commit=False`, and a `get_session()` dependency that yields a session inside an `async with` block and closes it afterward.

#### Scenario: Session dependency yields and cleans up

- **WHEN** a caller depends on `get_session()`
- **THEN** it receives an open `AsyncSession`, and the session is closed automatically when the caller finishes, even if an exception is raised

#### Scenario: Attributes remain accessible after commit

- **WHEN** an entity is committed through a session created by the factory
- **THEN** its attributes remain accessible without triggering an expired-attribute reload, because `expire_on_commit` is `False`
