## 1. Database Configuration

- [x] 1.1 Create `energyhub/shared/infrastructure/persistence/database.py` with a `Base(DeclarativeBase)` class
- [x] 1.2 Create the async engine from `settings.database_url` with `echo=settings.debug` and `future=True`
- [x] 1.3 Create `async_session_maker` via `async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)`
- [x] 1.4 Implement the `get_session()` dependency that `yield`s an `AsyncSession` inside `async with` and closes it
- [x] 1.5 Confirm the module imports cleanly (`poetry run python -c "import energyhub.shared.infrastructure.persistence.database"`)

## 2. ORM Entity Mapping

- [x] 2.1 Define/verify a shared mapped `BaseEntity` (from `Base`) with `id` PK and `created_at`/`updated_at` columns
- [x] 2.2 Map auth entities (`User`, `Role`, `Permission`) and the `user_roles`/`role_permissions` associations with typed `Mapped[...]` columns and unique constraints
- [x] 2.3 Map clients entities (`Client`, `Contact`) with the `Client`↔`Contact` relationship and `cnpj` uniqueness
- [x] 2.4 Map `Contract` with `client_id` FK, status/type, dates, and `Numeric` monetary columns
- [x] 2.5 Map remaining entities (`Negotiation`, `EnergyTransaction`, `Invoice`, `Payment`, `AuditLog`, `Notification`, `Report`) to their Fase 4 tables
- [x] 2.6 Declare relationships and the indexes needed for primary lookup paths, aligned to the Fase 4 schema
- [x] 2.7 Start the app (`poetry run uvicorn energyhub.main:app --reload`) and confirm no mapper/relationship errors in the logs

## 3. Generic Repository

- [x] 3.1 Create `shared/infrastructure/persistence/sqlalchemy_repository.py` with `SQLAlchemyRepository[T, ID]` taking `(session, entity_type)`
- [x] 3.2 Implement `save` (add + flush so the generated `id` is populated, return the entity)
- [x] 3.3 Implement `find_by_id` (returns the entity or `None`) and `find_all`
- [x] 3.4 Implement `delete` and `exists_by_id`

## 4. Entity Repositories

- [x] 4.1 Create `auth/infrastructure/persistence/` repositories: `UserRepository` (`find_by_username`, `find_by_email`, `exists_by_username`, `exists_by_email`, `find_by_role_name`)
- [x] 4.2 Add `RoleRepository` and `PermissionRepository` with `find_by_name`/`exists_by_name`
- [x] 4.3 Create `clients/infrastructure/persistence/` repositories: `ClientRepository` (`find_by_cnpj`, `exists_by_cnpj`, `find_by_active_true`, `search_by_name`, `find_by_location`)
- [x] 4.4 Add `ContactRepository` (`find_by_client_id`, `find_by_client_id_and_type`)
- [x] 4.5 Create repositories for the remaining modules: `ContractRepository`, `NegotiationRepository`, `EnergyTransactionRepository`, `InvoiceRepository`, `PaymentRepository`, `AuditLogRepository`, `NotificationRepository`, `ReportRepository` with their entity-specific finders

## 5. Query Filters

- [x] 5.1 Create `ClientFilter` in `clients/infrastructure/persistence/` with composable predicate methods (`has_cnpj`, `has_corporate_name`, `is_active`, `has_city`, `has_state`, `with_contact_type`)
- [x] 5.2 Create `ContractFilter` in `contracts/infrastructure/persistence/` (`has_contract_number`, `has_client_id`, `has_status`, `has_type`, `is_active_between`, `expiring_before`)
- [x] 5.3 Add filter-based query methods on the relevant repositories that combine predicates via `and_`/`or_`
- [x] 5.4 Create filters for the other modules as their query needs require

## 6. Pagination

- [x] 6.1 Create `PageRequest` in `shared/application/dto/` with `page`/`size`/`sort`/`direction` and `get_offset()`/`get_limit()`
- [x] 6.2 Create generic `PageResponse[T]` in `shared/application/dto/` with `create()` computing `total_pages`, `first`, `last`
- [x] 6.3 Add paginated repository methods that apply offset/limit and run a `count()` for total elements

## 7. Filter DTOs

- [x] 7.1 Create `ClientFilterDTO` (Pydantic) in `clients/application/dto/` with optional criteria fields
- [x] 7.2 Create `ContractFilterDTO` (Pydantic) in `contracts/application/dto/` with optional criteria fields (including date ranges)
- [x] 7.3 Translate set DTO fields into filter predicates in the corresponding repository query methods
- [x] 7.4 Create filter DTOs for the other modules as needed

## 8. Persistence Integration Tests

- [x] 8.1 Add an async session fixture (test database) with per-test isolation (transaction rollback or truncate) in `tests/`
- [x] 8.2 Add a CRUD test: save a `Client` via `ClientRepository` and assert generated `id` and persisted fields
- [x] 8.3 Add a finder test: save then `find_by_cnpj` returns the matching client
- [x] 8.4 Add filter and pagination tests asserting bounded page size and correct total count
- [x] 8.5 Run `poetry run pytest tests/` and confirm the suite passes

## 9. Validation

- [x] 9.1 Confirm all repositories exist for every entity and the app starts with no mapping errors
- [x] 9.2 Verify data is persisted and read back correctly against the Dockerized PostgreSQL
- [x] 9.3 Verify custom finders, filters, and pagination return the expected results
- [x] 9.4 Run `openspec validate implement-fase-5` and confirm the change is valid
