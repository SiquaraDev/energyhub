## Why

Fase 5 delivered the persistence layer (ORM mappings and repositories), but the application still has no business logic and no way to invoke it: nothing validates input, applies rules, or exposes an HTTP surface. This phase builds the application and presentation layers — DTOs, mappers, services, use cases, domain exceptions, and REST routers — so the persisted entities become an actual, documented, callable API.

## What Changes

- Add request/response DTOs (Pydantic models) per module (`auth`, `clients`, `contracts`, `negotiations`, `financial`, plus the remaining domains) in each module's `application/dto/`, with field constraints and self-describing schema metadata.
- Add reusable custom validators (e.g. `CnpjValidator`) in `shared/application/validation/`, applied to DTOs via `@field_validator`, so cross-cutting input rules live in one place.
- Add mappers per module in `application/mapper/` that translate between domain entities and DTOs (`to_entity`, `to_response_dto`), keeping the two representations decoupled.
- Add a domain exception hierarchy per module (`user_already_exists_exception`, `client_not_found_exception`, `invalid_cnpj_exception`, `invalid_contract_status_exception`, …) on top of the shared `ResourceNotFoundException`/`ValidationException`.
- Add application services in `application/service/` holding the business logic (existence checks, password hashing, role resolution, contact assembly, update semantics) over the Fase 5 repositories.
- Add use cases in `application/usecase/` extending the shared `UseCase[Input, Output]` contract that orchestrate a single business operation over the services.
- Add REST routers in `presentation/router/` extending `BaseRouter` that wire CRUD and listing endpoints to the services/use cases and return DTOs.
- Document every endpoint and DTO through FastAPI's OpenAPI/Swagger output (field/endpoint descriptions, API title/version) served at `/docs` and `/redoc`.

## Capabilities

### New Capabilities

- `request-response-dtos`: Pydantic request/response DTOs per entity with typed fields, constraints, and OpenAPI schema metadata for API input and output.
- `input-validation`: Reusable custom validators (CNPJ and other domain rules) in the shared layer, applied to DTOs so invalid input is rejected before it reaches services.
- `entity-dto-mappers`: Per-module mappers that convert between domain entities and DTOs in both directions, isolating the persistence model from the API contract.
- `domain-exceptions`: A domain-specific exception hierarchy (not-found, already-exists, invalid-state) per module, layered on shared base exceptions, to signal business-rule violations.
- `application-services`: Services encapsulating the business logic for each aggregate (create/find/update/delete with existence checks and domain rules) over the Fase 5 repositories.
- `use-case-orchestration`: Single-purpose use cases implementing the shared `UseCase[Input, Output]` contract that orchestrate one business operation via the services.
- `rest-api-endpoints`: REST routers exposing CRUD and paginated listing endpoints per module, returning DTOs and self-documented through FastAPI's OpenAPI/Swagger schema.

### Modified Capabilities

None — this phase introduces the application and presentation layers; no previously specified requirements change.

## Impact

- **Dependencies**: Uses `fastapi`, `pydantic`/`pydantic[email]`, and `passlib[bcrypt]` (declared in `pyproject.toml` from Fase 1) for routing, DTO validation, and password hashing.
- **Consumes**: The repositories and ORM entities from Fase 5, the pagination DTOs (`PageRequest`/`PageResponse`), the shared `BaseDTO`, `UseCase`, and `BaseRouter` abstractions from Fase 2, and `energyhub.config.settings` for the API metadata.
- **Provides**: The application layer (DTOs, mappers, services, use cases, domain exceptions) and the presentation layer (REST routers) that Fase 7 (Security) will protect with authentication/authorization.
- **New artifacts**: Per-module `application/dto/`, `application/mapper/`, `application/service/`, `application/usecase/`, and `domain/exception/`, plus `presentation/router/`; and shared `application/validation/`.
- **API surface**: First externally callable HTTP endpoints and the OpenAPI documentation at `/docs`/`/redoc`; endpoints are unauthenticated in this phase — access control is added in Fase 7.
