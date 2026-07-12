## Why

Fase 3 modeled the domain entities and Fase 4 created the physical PostgreSQL schema, but nothing in the application can yet read or write those tables. This phase builds the persistence layer — SQLAlchemy ORM mappings, an async session, and repositories — so use cases (Fase 6) have a typed, testable API to query and mutate data instead of hand-writing SQL everywhere.

## What Changes

- Add the async database configuration in `energyhub/shared/infrastructure/persistence/database.py`: a `DeclarativeBase` (`Base`), an async engine bound to `settings.database_url`, an `async_sessionmaker` with `expire_on_commit=False`, and a `get_session()` dependency that yields an `AsyncSession`.
- Map every domain entity (auth, clients, contracts, negotiations, financial, audit, notifications, reports) to its table via SQLAlchemy, all extending a shared `BaseEntity` (id + `created_at`/`updated_at`), with columns, relationships, and indexes validated at application startup.
- Add a generic async `SQLAlchemyRepository[T, ID]` base providing CRUD (`save`, `find_by_id`, `find_all`, `delete`, `exists_by_id`).
- Add a concrete repository per entity (`UserRepository`, `RoleRepository`, `PermissionRepository`, `ClientRepository`, `ContactRepository`, `ContractRepository`, `NegotiationRepository`, `EnergyTransactionRepository`, `InvoiceRepository`, `PaymentRepository`, `AuditLogRepository`, `NotificationRepository`, `ReportRepository`) with domain-specific finder methods (e.g. `find_by_username`, `find_by_cnpj`, `search_by_name`).
- Add reusable query-filter helpers (`ClientFilter`, `ContractFilter`, …) that build composable SQLAlchemy conditions, plus Pydantic filter DTOs (`ClientFilterDTO`, `ContractFilterDTO`, …) for advanced, optional-field filtering.
- Add generic pagination primitives `PageRequest`/`PageResponse` in `shared/application/dto/` and paginated (offset/limit + total count) repository queries.
- Add integration tests that validate save, finders, filtering, and pagination against a real (test) database.

## Capabilities

### New Capabilities

- `sqlalchemy-database-configuration`: Async engine, `Base` (`DeclarativeBase`), `async_sessionmaker`, and a `get_session()` dependency wired to application settings.
- `orm-entity-mapping`: Every domain entity mapped to its table via SQLAlchemy — shared `BaseEntity`, columns, relationships, and indexes — with the mapping validated at startup.
- `generic-repository`: A reusable async `SQLAlchemyRepository[T, ID]` base providing standard CRUD operations for any mapped entity.
- `entity-repositories`: One concrete repository per domain entity exposing entity-specific query methods on top of the generic base.
- `query-filtering`: Reusable SQLAlchemy filter/specification classes and Pydantic filter DTOs enabling composable, optional-criteria queries.
- `pagination`: Generic `PageRequest`/`PageResponse` DTOs and paginated repository queries that return content plus total/page metadata.
- `persistence-integration-tests`: Integration tests exercising CRUD, custom finders, filtering, and pagination against a database.

### Modified Capabilities

None — this phase introduces the persistence layer; no previously specified requirements change.

## Impact

- **Dependencies**: Uses `sqlalchemy` and `asyncpg` (already in `pyproject.toml` from Fase 1). Adds `pydantic` for filter DTOs (via FastAPI) and a test dependency (`pytest`, `pytest-asyncio`) if not already present.
- **Consumes**: Domain entities from Fase 3 and the physical schema/tables from Fase 4; reads `energyhub.config.settings.database_url` and `settings.debug`.
- **Provides**: `energyhub.shared.infrastructure.persistence.database.Base` and `get_session`, the repository classes, and the pagination/filter DTOs that Fase 6 use cases will depend on.
- **New artifacts**: `shared/infrastructure/persistence/` (database config + generic repository), `shared/application/dto/` (pagination), and per-module `infrastructure/persistence/` (repositories, filters) and `application/dto/` (filter DTOs).
- **Coordination**: `Base.metadata` here is the ORM counterpart of the Fase 4 migrations; the migrations remain the source of truth for schema and the ORM models are reconciled to them (no `--autogenerate`-driven schema changes in this phase).
