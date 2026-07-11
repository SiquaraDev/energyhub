## Why

Fase 7 secured the API and Fase 6/7 wired up the routers, but the API is still opaque to the humans and tools that consume it: there is no curated OpenAPI document, endpoints carry no summaries or response contracts, error payloads are undocumented, and there are no worked examples. This phase turns the running FastAPI app into a self-describing, discoverable product — a customized OpenAPI schema, richly documented endpoints and schemas, standardized error responses, an error catalog, and usage examples — so integrators can understand and call the API without reading the source.

## What Changes

- Customize the FastAPI OpenAPI document in `energyhub/main.py`: set title/description/version, expose `/docs` (Swagger UI), `/redoc`, and `/openapi.json`, and add a `custom_openapi()` builder that injects contact/license metadata and a `bearerAuth` JWT security scheme applied globally.
- Document every endpoint at the router level with `summary`, `description`, and per-status `responses`, and group endpoints into OpenAPI tags (`Authentication`, `Clients`, …) when routers are included.
- Enrich Pydantic request/response DTOs with `Field(description=..., example=...)`, constraints (`min_length`, `EmailStr`, etc.), so schemas render with descriptions and example payloads in the docs.
- Add standardized error response schemas (`ErrorResponse`, `ValidationErrorResponse`/`FieldError`) in `shared/presentation/response/` and update the global exception handlers to return them, so documented error bodies match runtime behavior.
- Add an `error_code` attribute to domain exceptions and author `docs/API_ERRORS.md` cataloging HTTP status codes, their causes, and module-specific error codes (auth, clients, contracts, …).
- Author `docs/API_EXAMPLES.md` with copy-pasteable `curl` request/response examples for the primary flows (login, create/list/get client, …).

## Capabilities

### New Capabilities

- `openapi-configuration`: A customized OpenAPI document with API metadata, contact/license info, a global `bearerAuth` JWT security scheme, and Swagger UI / ReDoc / raw JSON endpoints exposed.
- `endpoint-documentation`: Router-level `summary`, `description`, documented per-status `responses`, and OpenAPI tags grouping endpoints by module.
- `schema-documentation`: Pydantic DTOs annotated with field descriptions, constraints, and examples so request/response schemas are self-describing in the docs.
- `error-response-schemas`: Standardized `ErrorResponse` and `ValidationErrorResponse` models plus exception handlers that emit them, giving every error a documented, consistent shape.
- `error-catalog`: A maintained `docs/API_ERRORS.md` and `error_code`-bearing exceptions cataloging generic HTTP errors and module-specific error codes.
- `api-usage-examples`: A `docs/API_EXAMPLES.md` guide with `curl` request/response examples for the core API flows.

### Modified Capabilities

None — this phase adds documentation and standardized error surfaces over the existing API; no previously specified requirement changes behavior.

## Impact

- **Dependencies**: No new packages — relies on FastAPI's built-in OpenAPI/Swagger support and Pydantic already declared in `pyproject.toml`.
- **Consumes**: The routers and DTOs from Fase 6, the security/`get_current_user` dependency and global exception handling from Fase 7, and `energyhub.config.settings`.
- **Provides**: A published OpenAPI contract (`/openapi.json`, `/docs`, `/redoc`), reusable error response schemas, and reference docs (`API_ERRORS.md`, `API_EXAMPLES.md`) that downstream clients and later phases build on.
- **Modified artifacts**: `energyhub/main.py` (OpenAPI builder, tag/handler registration), existing routers (route metadata), and existing DTOs (`Field` annotations).
- **New artifacts**: `shared/presentation/response/` error models, updated exception handlers, `docs/API_ERRORS.md`, and `docs/API_EXAMPLES.md`.
