## Context

Fase 3 modeled the domain, Fase 4 built the schema, and Fase 5 delivered ORM mappings, repositories, filters, and pagination. What is still missing is everything above persistence: input validation, business rules, orchestration, error semantics, and an HTTP surface. This phase fills the application and presentation layers of the existing Clean Architecture layout so the persisted entities become a documented, callable API.

The stack is fixed by `pyproject.toml`: FastAPI + Pydantic v2, `passlib[bcrypt]` for password hashing, Python ≥3.12. The layer boundaries were established in Fase 2 (shared `BaseDTO`, `UseCase[Input, Output]`, `BaseRouter`, `PageRequest`/`PageResponse`) and this phase must respect them: `presentation → application → domain`, with `infrastructure` (Fase 5 repositories) consumed by application services. Everything is additive; no schema change and no touching of the Fase 5 persistence code.

This phase is intentionally unauthenticated — access control, tokens, and dependency-injected security are Fase 7. The endpoints built here are the surface that Fase 7 will later protect.

## Goals / Non-Goals

**Goals:**
- Provide request/response DTOs per entity with field constraints and OpenAPI metadata.
- Centralize cross-cutting input rules as reusable validators applied to DTOs.
- Provide per-module mappers isolating the ORM entity from the API contract.
- Provide a domain exception hierarchy layered on the shared base exceptions.
- Provide application services (business logic) and thin use cases (orchestration) over the Fase 5 repositories.
- Expose REST routers per module returning DTOs, self-documented via OpenAPI at `/docs`/`/redoc`.

**Non-Goals:**
- No authentication, authorization, tokens, or password/login flows beyond hashing on user creation (Fase 7).
- No schema changes and no changes to Fase 5 repositories, ORM mappings, or migrations.
- No new persistence patterns (caching, background jobs, event publishing).
- No frontend or client SDK; only the server-side API and its generated documentation.
- No exhaustive endpoint set for every conceivable operation — CRUD + paginated listing per aggregate, extended per module as the plan requires.

## Decisions

**Layer the application into DTO → mapper → service → use case, with routers on top:**
- **Decision:** Keep the five distinct roles the plan prescribes — DTOs (transport/validation), mappers (entity↔DTO), services (business logic over repositories), use cases (single-operation orchestration implementing `UseCase[Input, Output]`), routers (HTTP wiring) — each in its module folder.
- **Rationale:** Matches the Fase 2 boundaries and the plan's examples; each layer is independently testable and swappable, and business logic stays out of routers and out of DTOs.
- **Alternative considered:** Collapse services and use cases into one layer (call services directly from routers) — rejected because the shared `UseCase` contract is already established and use cases give a uniform, mockable entry point for Fase 7 to wrap with authorization.

**Single ORM/domain model reused across layers; mappers only translate to DTOs:**
- **Decision:** Mappers convert between the Fase 5 mapped entities and DTOs; there is no separate "domain model vs. persistence model" split.
- **Rationale:** Fase 5 chose single-model persistence (entities are the ORM models); introducing a third representation here would add translation boilerplate with no consumer needing it. DTOs already decouple the API contract from the entity.
- **Alternative considered:** Full hexagonal purity with domain models distinct from ORM models — rejected as premature, consistent with the Fase 5 decision.

**Domain exceptions extend shared base exceptions; a single boundary maps them to HTTP:**
- **Decision:** Each module raises typed domain exceptions (not-found, already-exists, invalid-state) that extend `ResourceNotFoundException`/`ValidationException`; a central exception handler translates base types to HTTP status codes (404, 409/422).
- **Rationale:** Services signal rule violations by type, not by null or ad-hoc HTTP raises, so mapping to HTTP is centralized and consistent, and Fase 7 can add auth exceptions to the same scheme.
- **Alternative considered:** Raise `HTTPException` directly in services — rejected; it couples business logic to the web framework and violates the layer boundary.

**Transaction boundary stays at the request-scoped session from Fase 5:**
- **Decision:** Services call repositories that `flush` but do not `commit`; the request-scoped `get_session()` from Fase 5 owns commit/rollback, so a use case that touches multiple repositories composes into one transaction.
- **Rationale:** Preserves the Fase 5 unit-of-work decision (`expire_on_commit=False`, commit at the edge) and enables atomic multi-entity operations (e.g. create client + contacts).
- **Alternative considered:** Commit inside each service method — rejected; it fragments transactions and breaks atomicity.

**Password hashing lives in the user service, not in a DTO or mapper:**
- **Decision:** Hash passwords with `passlib` (`bcrypt`) inside `UserService` on create/update; DTOs carry the plaintext only as validated input and response DTOs never expose it.
- **Rationale:** Hashing is a business rule, not a transport concern; keeping it in the service keeps mappers pure and prevents the password from leaking into any response.
- **Alternative considered:** Hash in the mapper's `to_entity` — rejected; mixes a security policy into a translation utility and makes update-vs-create semantics awkward.

**OpenAPI documentation is derived, not hand-written:**
- **Decision:** Drive documentation from Pydantic `Field(..., description=...)` metadata and per-route `summary`/`description`, plus FastAPI app-level title/description/version, served at `/docs`/`/redoc`.
- **Rationale:** FastAPI generates the schema automatically; investing in field/endpoint descriptions keeps documentation in sync with code at zero extra maintenance.
- **Alternative considered:** Maintaining a separate OpenAPI/Markdown document — rejected as duplicative and prone to drift.

## Risks / Trade-offs

- **Upstream layers not yet materialized in code** → This phase depends on Fase 5 repositories, entities, and the shared `BaseDTO`/`UseCase`/`BaseRouter`. If those are not present, they are established/verified as part of wiring this layer, keeping imports resolvable; do not fork or reimplement Fase 5 abstractions here.
- **Unauthenticated endpoints in the interim** → The API is fully open until Fase 7. Mitigation: treat this phase's deployments as non-public; document that access control is deferred and design the routers so a security dependency can be injected without reshaping them.
- **DTO/entity field drift** → DTOs and mappers duplicate field lists; a field added to an entity can be silently omitted from a DTO. Mitigation: keep mapper conversions total (assign every response field) and cover create/read round-trips with tests so omissions surface.
- **Inconsistent error responses** → Without a central handler, each router could map errors differently. Mitigation: one exception-handling boundary keyed on the shared base exception types.
- **Naive `find_all` counting** → The plan's example computes `total` from the fetched list; that is wrong for real pagination. Mitigation: back listing with the Fase 5 paginated query (bounded `select` + `count()`), not `len(page_content)`.
- **CNPJ/email validation strictness** → Overly strict validators can reject legitimate values; overly loose ones let bad data through. Mitigation: validators are standalone and unit-tested, so the rule can be tuned in one place.

## Migration Plan

1. Add request/response DTOs and the shared custom validators; confirm they import and validate sample payloads.
2. Add the domain exception hierarchy per module, extending the shared base exceptions.
3. Add mappers per module and verify entity↔DTO round-trips (including nested relations).
4. Add services over the Fase 5 repositories, then the use cases delegating to them.
5. Add routers extending `BaseRouter`, wire them into the FastAPI app, and register the central exception handler.
6. Configure API metadata and field/endpoint descriptions; start the app (`poetry run uvicorn energyhub.main:app --reload`) and confirm `/docs` renders the endpoints.
7. Rollback: this phase is additive application/presentation code with no schema change; reverting the branch removes the API layer without touching the database or Fase 5 code.

## Open Questions

- Should repositories be injected into services as concrete classes or via `Protocol`/ABC interfaces for Fase 7 test doubles? (Current plan: concrete now, extract protocols if security tests need them.)
- Which update semantics apply — partial (PATCH-style, only set fields) or full replacement (PUT)? The plan mixes both; confirm per aggregate when building routers.
- Should the central exception handler live in `shared/presentation/` in this phase or be finalized alongside Fase 7's auth exceptions? (Leaning: minimal handler now, extended in Fase 7.)
- Default and maximum page sizes for list endpoints — the plan uses `size=20` with a `le=100` bound; confirm the hard maximum.
