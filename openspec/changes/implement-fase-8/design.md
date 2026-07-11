## Context

By Fase 7 the EnergyHub API runs with authentication, global exception handling, and per-module routers. What is missing is a consumer-facing contract: FastAPI auto-generates an OpenAPI document, but out of the box it carries no curated metadata, no operation summaries, no documented response codes, no schema descriptions or examples, and no worked usage guide. Error bodies returned at runtime are not described anywhere, so a client cannot know their shape without triggering them.

The stack is fixed: FastAPI (with built-in OpenAPI/Swagger + ReDoc) and Pydantic, both already in `pyproject.toml`. This phase is almost entirely additive metadata and documentation — it changes how the existing API describes itself, not what it does. The one behavioral surface it touches is standardizing error response bodies so they match what is documented. Configuration remains single-sourced through `energyhub.config.settings`.

This phase depends on Fase 6 routers/DTOs and Fase 7 security and global exception handling; it produces the published OpenAPI contract and reference docs that external integrators and later phases consume.

## Goals / Non-Goals

**Goals:**
- Publish a customized OpenAPI document (metadata, contact/license, global `bearerAuth` JWT scheme) with Swagger UI, ReDoc, and raw JSON endpoints exposed.
- Document every endpoint with summary, description, documented per-status responses, tags, and query-parameter descriptions.
- Make Pydantic DTOs self-describing with field descriptions, constraints, and examples.
- Standardize error responses (`ErrorResponse`, `ValidationErrorResponse`) and align exception handlers to emit them.
- Provide an error catalog (`docs/API_ERRORS.md`) and a usage guide (`docs/API_EXAMPLES.md`).

**Non-Goals:**
- No new endpoints, business logic, or changes to successful response payloads (Fase 6 owns those).
- No new authentication/authorization behavior — only documentation of the existing `bearerAuth` scheme.
- No external documentation hosting, SDK/client generation, or API versioning strategy beyond the declared version string.
- No changes to the persistence or domain layers.

## Decisions

**Customize OpenAPI via a cached `custom_openapi()` override rather than per-route `openapi_extra`:**
- **Decision:** Override `app.openapi` with a `custom_openapi()` function that builds the schema once (guarded by `app.openapi_schema`), injects `contact`/`license` and the `bearerAuth` security scheme, and caches the result.
- **Rationale:** Cross-cutting metadata (contact, license, global security) belongs in one place; caching avoids rebuilding the schema on every `/openapi.json` hit. This is FastAPI's documented extension point.
- **Alternative considered:** Sprinkling `openapi_extra` and security config across individual routes — rejected as scattered and hard to keep consistent for document-level fields.

**Document routes through the existing `BaseRouter` / `add_api_route` metadata, not decorators:**
- **Decision:** Supply `summary`, `description`, and `responses` as arguments to `add_api_route` where routes are already registered, and pass `tags` when routers are included in `main.py`.
- **Rationale:** The Fase 6 routers are class-based and register routes imperatively; adding metadata inline keeps documentation next to the route definition without restructuring the router pattern.
- **Alternative considered:** Refactoring to decorator-style `@router.post(...)` endpoints to attach docs — rejected as an unnecessary rewrite of the established router style.

**Standardize error bodies with dedicated response models and align handlers to them:**
- **Decision:** Introduce `ErrorResponse` and `ValidationErrorResponse`/`FieldError` models in `shared/presentation/response/`, and have the global handlers serialize these models. Document them as the `responses` for error statuses.
- **Rationale:** A documented error schema is only trustworthy if the runtime body matches it; centralizing the shape guarantees consistency across modules and makes `4xx`/`5xx` responses predictable for clients.
- **Alternative considered:** Returning ad-hoc dicts from handlers and hand-writing matching docs — rejected because the docs and reality drift apart over time.

**Add a machine-readable `error_code` to domain exceptions:**
- **Decision:** Give domain exceptions an `error_code` attribute with a sensible default, and catalog those codes in `docs/API_ERRORS.md`.
- **Rationale:** Human-readable messages are not stable identifiers; an `error_code` lets clients branch on failures without string-matching. Backward compatible because it defaults.
- **Alternative considered:** Encoding codes only in the message string — rejected as brittle and unfriendly to programmatic handling.

**Examples via Pydantic `Field(example=...)` plus a hand-authored markdown guide:**
- **Decision:** Use `Field(example=...)` so Swagger UI shows example payloads automatically, and complement it with `docs/API_EXAMPLES.md` for end-to-end `curl` flows (including the bearer header).
- **Rationale:** Field examples keep in-schema examples close to the code and always in sync; the markdown guide covers multi-step flows (auth then call) that per-field examples cannot express.
- **Alternative considered:** Only external markdown examples — rejected because in-UI examples materially improve the "try it out" experience and stay attached to the schema.

## Risks / Trade-offs

- **Documentation drift** (docs describe routes/DTOs that later change) → Keep route metadata beside the route definition and DTO examples on the fields themselves so they move with the code; the error catalog is the only free-standing artifact and is small.
- **Documented responses not matching runtime bodies** → Standardizing handlers on `ErrorResponse`/`ValidationErrorResponse` is the mitigation: document the same models the handlers emit rather than describing responses independently.
- **Exposing `/docs` and `/openapi.json` publicly leaks the API surface** → Acceptable for this phase; if the environment requires it, gating the docs endpoints (e.g. disabling in production or requiring auth) is a follow-up, noted as an open question.
- **Field examples containing realistic-looking secrets/PII** (tokens, CNPJs, emails) → Use clearly synthetic placeholder values in examples so nothing sensitive is embedded in the published schema or guide.
- **`custom_openapi()` caching hides late route additions** → Because the schema is built once, routes must be registered before first schema access; this holds for the normal app-startup flow and is documented.

## Migration Plan

1. Add the `custom_openapi()` builder and app metadata in `main.py`; start the app and confirm `/docs`, `/redoc`, and `/openapi.json` render with contact/license and the `bearerAuth` scheme.
2. Add `summary`/`description`/`responses` to each route and `tags` at router inclusion; reload and confirm grouping and response docs.
3. Annotate DTO fields with descriptions, constraints, and examples; confirm schemas and example payloads render.
4. Add `ErrorResponse`/`ValidationErrorResponse` models, align the global handlers to emit them, and document them as error responses; trigger a `404` and a validation error to confirm bodies match.
5. Add `error_code` to exceptions and author `docs/API_ERRORS.md` and `docs/API_EXAMPLES.md`.
6. Rollback: this phase is additive metadata and documentation; reverting the branch restores the prior (auto-generated) docs and error bodies with no data or schema impact.

## Open Questions

- Should `/docs`, `/redoc`, and `/openapi.json` be disabled or auth-gated in production, or remain open? (Current plan: open; revisit per deployment environment.)
- Should the OpenAPI `version` track the application version from a single source (e.g. `pyproject.toml`) rather than a hardcoded string? (Deferred; hardcoded `1.0.0` for now.)
- Do we want machine-readable error codes echoed in the `ErrorResponse` body (an `error_code` field), or is the message plus HTTP status sufficient for now? (To confirm alongside client needs.)
