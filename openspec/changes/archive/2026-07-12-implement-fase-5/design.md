## Context

Fase 3 modeled the domain (entities, value objects, enums) and Fase 4 authored the PostgreSQL schema as explicit Alembic migrations. Neither produced a runtime data-access path: there is no async engine, no ORM mapping, and no repositories. This phase adds that layer inside the existing Clean Architecture layout, so Fase 6 use cases depend on repository interfaces rather than raw SQL.

The stack is fixed by `pyproject.toml`: SQLAlchemy 2.x (async), asyncpg, FastAPI/Pydantic, Python ≥3.12. The database schema already exists from Fase 4 and is the source of truth; the ORM models here are reconciled to it. Configuration is single-sourced through `energyhub.config.settings` (`database_url`, `debug`).

A note on ordering: Fase 4 migrations conceptually target `Base.metadata`, but the concrete `Base`, engine, and session live here (Fase 5, `shared/infrastructure/persistence/database.py`). This phase owns those objects; the migrations remain hand-authored and independent, so there is no hard build-time coupling to resolve — only conceptual alignment between ORM metadata and the migrated schema.

## Goals / Non-Goals

**Goals:**
- Provide async database configuration: `Base`, engine, `async_sessionmaker`, and a `get_session()` dependency.
- Map every domain entity to its Fase 4 table with correct types, relationships, and indexes; validate mappers load at startup.
- Provide a generic async `SQLAlchemyRepository[T, ID]` and one concrete repository per entity with domain-specific finders.
- Provide composable query filters and Pydantic filter DTOs, plus generic `PageRequest`/`PageResponse` pagination.
- Validate the layer with integration tests covering CRUD, finders, filtering, and pagination.

**Non-Goals:**
- No use cases, services, or API endpoints (Fase 6+).
- No schema changes and no `--autogenerate` migrations — the schema is owned by Fase 4.
- No caching, read replicas, or query-performance tuning beyond the indexes already defined.
- No authentication/authorization logic (only the auth *entities* are persisted here).

## Decisions

**Single-model persistence via imperative (classical) mapping — preserving the pure domain:**
- **Decision:** Keep the Fase 3 domain entities as **pure dataclasses** (no SQLAlchemy imports) and map them to the Fase 4 tables with **imperative mapping** (`registry.map_imperatively(User, users_table, ...)`) in `shared/infrastructure/persistence/mapping.py`. Repositories still query the entities directly (`select(User).where(User.username == ...)`) because the mapper instruments them at runtime. `configure_mappings()` runs at app startup (and in the test fixture) to register and resolve the mappers.
- **Rationale:** A single model (no separate ORM classes) keeps the code small and matches the plan's direct-query examples, **while honoring the domain-purity rule established in Fase 3** (the domain MUST NOT import frameworks — enforced in the baseline and `ARCHITECTURE.md`). Entities also gain identity-based equality/hashing (`BaseEntity` `eq=False` + `__eq__`/`__hash__` by `id`) — the correct DDD semantics for entities and a requirement for ORM instances to be hashable.
- **Trade-off:** mypy cannot see the runtime SQLAlchemy instrumentation on the dataclasses, so query expressions (`User.username == ...`, `.ilike`, `.is_`) trigger false positives; these are suppressed **only** in the persistence layer via a scoped `mypy` override, and that layer is covered by integration tests against the real schema.
- **Alternatives considered:** (a) Declarative `Mapped[...]` columns on the entities — rejected: it forces SQLAlchemy into the domain, breaking purity (the original plan's premise that the entities "did not yet exist" no longer held). (b) Separate persistence models + domain↔model mappers (hexagonal) — rejected: doubles the class count and translation boilerplate with no consumer needing the decoupling yet.

**Generic base repository parameterized by entity + id type:**
- **Decision:** `SQLAlchemyRepository[T, ID]` holds the `AsyncSession` and entity type and implements `save`/`find_by_id`/`find_all`/`delete`/`exists_by_id`; concrete repositories subclass it and add finders.
- **Rationale:** Removes CRUD duplication across 13 repositories and gives one place to enforce flush/return conventions.
- **Alternative considered:** Standalone functions or a repository per entity with copy-pasted CRUD — rejected as repetitive and inconsistent.

**`save` flushes but does not commit:**
- **Decision:** Repository writes `add` + `flush` (to populate generated ids) but leave `commit` to the caller/unit-of-work (the request-scoped session).
- **Rationale:** Keeps transaction boundaries with the use case (Fase 6), so multiple repository calls compose into one transaction. `expire_on_commit=False` keeps entities usable after the outer commit.
- **Alternative considered:** Commit inside `save` — rejected; it fragments transactions and prevents atomic multi-entity operations.

**Filtering split into two layers — SQLAlchemy filter builders and Pydantic DTOs:**
- **Decision:** Infrastructure `*Filter` classes return composable SQL conditions; application `*FilterDTO` Pydantic models carry optional user-supplied criteria. Repositories translate a DTO into the conditions to apply.
- **Rationale:** Separates transport/validation (DTO, application layer) from query construction (infrastructure), respecting the layer boundaries established in Fase 2.
- **Alternative considered:** Build queries straight from DTOs in the repository — rejected; it leaks query-construction detail and duplicates predicate logic.

**Pagination via offset/limit with a total-count query:**
- **Decision:** `PageRequest` yields `offset`/`limit`; paginated queries run the bounded `select` plus a `count()` to fill `PageResponse` metadata (`total_pages`, `first`, `last`).
- **Rationale:** Simple, matches the plan, and is adequate for the expected data volumes; page metadata is computed once in `PageResponse.create`.
- **Alternative considered:** Keyset/cursor pagination — rejected as premature; offset/limit is sufficient and simpler for admin-style listings.

**Zero-based pages, `Numeric` for money:**
- **Decision:** Follow the plan's zero-based page numbering and use fixed-precision `Numeric` for monetary/quantity columns to mirror Fase 4.
- **Rationale:** Consistency with the plan and with the migrated schema; avoids float rounding on money.

## Risks / Trade-offs

- **Domain entities already exist as pure dataclasses (Fase 3)** → They are mapped here **without modification to their purity** (imperative mapping in infrastructure); the only domain change is `BaseEntity` adopting identity-based equality/hashing. Keep mappings aligned to the Fase 4 tables, which are the source of truth.
- **ORM/migration drift** (types, nullability, names diverge from Fase 4) → Reconcile ORM to migrations, not the reverse; a mapping-vs-schema check (startup mapper resolution + integration tests against the real schema) catches divergence early.
- **`find_all` / unbounded queries on large tables** → Prefer paginated methods for listing endpoints; treat `find_all` as an internal/small-set convenience, and default list APIs to pagination.
- **`expire_on_commit=False` returns potentially stale attributes** → Acceptable trade-off for async ergonomics; callers that need fresh data re-query. Documented so it is a deliberate choice, not a surprise.
- **Integration tests need a database** → Provide an async session fixture with per-test isolation (transaction rollback or truncate) so the suite is deterministic; document how to point tests at the Dockerized PostgreSQL / a disposable test database.
- **`search_by_name` uses `LOWER(...) LIKE` scans** → Fine at current volume; if it becomes hot, add a trigram or functional index later (out of scope here).

## Migration Plan

1. Add `database.py` (`Base`, engine, session factory, `get_session`) and confirm the app imports it without error.
2. Map entities to the Fase 4 tables and start the app (`uvicorn energyhub.main:app --reload`) to confirm mappers resolve with no errors.
3. Add the generic repository, then the per-entity repositories with their finders.
4. Add filters, filter DTOs, and pagination DTOs; wire paginated/filter query methods into repositories.
5. Add integration tests (session fixture + CRUD/finder/filter/pagination cases) and run `poetry run pytest`.
6. Rollback: this phase is additive code with no schema change; reverting the branch removes the layer without touching the database.

## Open Questions

- Should repositories expose interfaces (ABCs/`Protocol`s) in the domain layer now for Fase 6 dependency inversion, or is a concrete-class dependency acceptable until use cases exist? (Current plan: concrete classes now; extract protocols in Fase 6 if needed.)
- Which entities need soft-delete vs. hard `delete`? (Deferred; `delete` is hard-delete unless a domain requirement says otherwise.)
- Default page size and maximum page size for list endpoints — plan uses `size=20`; a hard upper bound to be confirmed when endpoints are built in Fase 6.
