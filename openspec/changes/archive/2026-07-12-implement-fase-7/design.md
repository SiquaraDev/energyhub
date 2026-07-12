## Context

Fase 6 delivered the use cases and FastAPI routers that expose EnergyHub's domain operations, but the API is unauthenticated: every endpoint is publicly callable. The building blocks for access control already exist upstream — the `User`, `Role`, and `Permission` entities were modeled in Fase 3 and mapped in Fase 5, and Fase 4 seeded the default roles (`ADMIN`, `OPERATOR`, `CLIENT`), the base permissions, the ADMIN grants, and a default admin user. What is missing is the runtime security layer that verifies identity and enforces those grants on each request.

This phase adds authentication and authorization inside the existing Clean Architecture layout. The stack is fixed by the plan: `python-jose[cryptography]` for JWT, `passlib[bcrypt]` for password hashing, and `python-multipart` for form-encoded credentials, all layered on FastAPI's dependency-injection and `HTTPBearer` security utilities. Configuration is single-sourced through `energyhub.config.settings` (`secret_key`, `algorithm`, `access_token_expire_minutes`).

The security concerns split cleanly across layers: password hashing and RBAC guards are cross-cutting and live in `shared/infrastructure/security/`; JWT handling, the current-user dependency, and `UserDetails` are auth-specific and live in `auth/infrastructure/security/`; the login flow and role/permission read services live in the auth application layer; and the wiring (CORS, public vs. protected routes, per-endpoint permissions) happens in `main.py` and the existing routers.

## Goals / Non-Goals

**Goals:**
- Verify identity with a stateless JWT issued at login and validated on every protected request.
- Hash and verify passwords with BCrypt; never store or compare plaintext.
- Enforce role- and permission-based access via reusable FastAPI dependencies (`require_permission`, `require_role`).
- Resolve a bearer token to a `UserDetails` that exposes the caller's roles and flattened permissions.
- Wire application-wide security: CORS, public auth routes vs. JWT-protected resource routes, and per-endpoint permission requirements.
- Provide read services over the roles/permissions seeded in Fase 4.

**Non-Goals:**
- No user self-registration, password-reset, refresh-token rotation, or token revocation/blacklist in this phase.
- No changes to the role/permission data model or the seed data (owned by Fase 3/4).
- No OAuth2/OIDC/social login or external identity providers.
- No rate limiting, brute-force lockout, or audit-logging of auth events beyond what already exists.
- No new domain use cases or endpoints — only the security overlay on the Fase 6 API.

## Decisions

**Stateless JWT (HS256) rather than server-side sessions:**
- **Decision:** Issue a signed JWT at login carrying `sub` (username) and `exp`; validate it on each request via `HTTPBearer` + `JwtService.decode_token`. No session store.
- **Rationale:** Matches the plan, keeps the API horizontally scalable with no shared session state, and fits FastAPI's dependency model. HS256 with a single secret is adequate for a single-service deployment.
- **Alternative considered:** Server-side sessions (or Redis-backed tokens) — rejected as unnecessary infrastructure for the current single-service scope; revisit if token revocation becomes a hard requirement.

**Password hashing and RBAC guards in `shared/infrastructure/security/`; JWT and current-user in `auth/infrastructure/security/`:**
- **Decision:** Place `get_password_hash`/`verify_password` and the `require_permission`/`require_role` factories in the shared layer, and `JwtService`, `UserDetails`, and `get_current_user` in the auth module.
- **Rationale:** Hashing and RBAC checks are cross-cutting and reused by any module; token handling and user loading are auth-specific and depend on the auth repositories. This respects the layer boundaries established in Fase 2.
- **Alternative considered:** Putting everything under `auth/` — rejected because the RBAC guards and hashing are consumed by non-auth routers, so a shared home avoids an inward dependency from `shared` to `auth`.

**Authorization expressed as FastAPI dependencies attached to routes, not a global middleware:**
- **Decision:** Protect route groups with `dependencies=[Depends(get_current_user)]` and gate individual operations with `Depends(require_permission("..."))`; auth routes are registered without those dependencies.
- **Rationale:** Per-route dependencies keep the public/protected boundary explicit and declarative, compose naturally with FastAPI's OpenAPI generation, and let each endpoint state the permission it needs. `require_permission` depends on `get_current_user`, so 401 (unauthenticated) is always resolved before 403 (unauthorized).
- **Alternative considered:** A single ASGI auth middleware inspecting paths — rejected; path-matching logic drifts from the routers and is harder to keep in sync than co-located dependencies.

**`UserDetails` wrapper computes roles/permissions from the loaded `User`:**
- **Decision:** Wrap the `User` entity in a `UserDetails` object that exposes `username`, `active`, `roles`, and a `permissions` property that flattens permission names across the user's roles.
- **Rationale:** Gives the guards a stable, security-focused view without leaking the ORM entity into the presentation layer, and centralizes the role→permission flattening in one place.
- **Alternative considered:** Passing the raw `User` entity to guards — rejected; it couples authorization logic to the persistence model and scatters permission-flattening across call sites.

**`sub` claim holds the username (business key), not the internal id:**
- **Decision:** Use the username as the token subject and reload the user by username in `get_current_user`.
- **Rationale:** Matches the plan's `extract_username`/`find_by_username` flow and keeps tokens readable; the reload guarantees the user still exists and is current on each request.
- **Alternative considered:** Embedding the user id (and optionally cached roles/permissions) in the token — rejected for now; reloading avoids stale authorization data when grants change mid-session, at the cost of one lookup per request.

**Role/permission access is exposed as read-only services:**
- **Decision:** `RoleService` and `PermissionService` provide `find_all`/`find_by_name`/`find_by_role_name` only; grants are managed through Fase 4 seed data and migrations, not runtime CRUD.
- **Rationale:** The phase's scope is enforcing existing grants, not administering them; read-only services satisfy introspection needs without opening a privilege-management surface.
- **Alternative considered:** Full role/permission management endpoints — deferred to a later phase if an admin UI needs them.

## Risks / Trade-offs

- **Default `secret_key` and seeded admin credentials** → The plan ships a placeholder `secret_key` and an `admin/admin123` seed account; both MUST be overridden via environment configuration before any non-local use. Documented as a required rotation step rather than a silent default.
- **No token revocation / short-lived tokens only** → A leaked token is valid until `exp`. Mitigation: keep `access_token_expire_minutes` modest (plan default 30) and treat refresh/revocation as a follow-up; do not embed long-lived secrets in tokens.
- **Reload-per-request cost** → Resolving the user on every protected request adds a DB lookup. Acceptable at current volumes and keeps authorization fresh; if it becomes hot, cache the `UserDetails` per request or embed a short-lived permission snapshot later.
- **CORS `allow_origins=["*"]` from the plan is permissive** → Fine for local development but must be narrowed to known origins (and reconciled with `allow_credentials`) before production.
- **Auth modules assume upstream entities/repositories exist** → `get_current_user` and `AuthenticationService` depend on the `User`/`Role`/`Permission` mappings (Fase 5) and repositories; if those are not materialized, the login path cannot resolve users. Keep the auth persistence contracts aligned with Fase 5.
- **`bcrypt` work factor vs. login latency** → BCrypt is intentionally slow; the default cost is a deliberate trade-off between hashing cost and resistance to offline cracking, and is acceptable for interactive login.

## Migration Plan

1. Add the security dependencies to `pyproject.toml` (`poetry add python-jose[cryptography] passlib[bcrypt] python-multipart`) and the JWT settings to `energyhub.config.settings`.
2. Add the shared password-hashing module and confirm `get_password_hash`/`verify_password` round-trip.
3. Add `JwtService` and verify create/decode/expiry against the configured settings.
4. Add the login flow (DTOs, `AuthenticationService`, `AuthRouter`) and register `/api/v1/auth` as a public route.
5. Add `UserDetails`, `get_current_user`, and the `require_permission`/`require_role` guards.
6. Wire CORS, protect the resource routers with `get_current_user`, and attach per-endpoint permission guards; add `RoleService`/`PermissionService`.
7. Validate end to end: log in to obtain a token, call a protected endpoint with and without the token, and confirm 401/403/200 behavior.
8. Rollback: this phase is additive; reverting the branch removes the security layer and restores the open API without touching the database or schema.

## Open Questions

- Should the login endpoint accept OAuth2 password-form (`OAuth2PasswordRequestBody`) for Swagger's built-in "Authorize" flow, or is the JSON `LoginRequestDTO` sufficient? (Plan uses JSON; `python-multipart` is added, so form support could be enabled later.)
- Do we need refresh tokens / token revocation in this phase, or is a single short-lived access token acceptable until a later phase? (Current plan: access token only.)
- Which resource routers beyond clients get explicit per-permission mapping now vs. a blanket `get_current_user` gate? (Plan details clients; other modules follow the same pattern as their endpoints are secured.)
- Final CORS allowed-origins list and whether `allow_credentials` is required for the intended frontend. (Deferred to deployment configuration.)
