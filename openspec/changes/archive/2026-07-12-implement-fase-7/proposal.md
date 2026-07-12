## Why

Fase 6 exposed the domain use cases through FastAPI routers, but every endpoint is currently open — anyone can read or mutate clients, contracts, and financial records without proving who they are or whether they are allowed to. This phase adds authentication (login + JWT) and authorization (role/permission-based access control), so identity is verified on every request and each operation is gated by the caller's granted permissions.

## What Changes

- Add a shared password module in `shared/infrastructure/security/` using BCrypt (`passlib`) with `get_password_hash` and `verify_password`.
- Add JWT configuration (`secret_key`, `algorithm`, `access_token_expire_minutes`) to `energyhub.config.settings` and a `JwtService` (python-jose) that creates, decodes, and validates signed access tokens and extracts the subject/username.
- Add the login flow: `LoginRequestDTO`/`LoginResponseDTO`, an `AuthenticationService` that verifies credentials and rejects unknown or inactive users, and an `AuthRouter` exposing `POST /api/v1/auth/login`.
- Add a `get_current_user` FastAPI dependency that resolves the bearer token to a `UserDetails` wrapper exposing the authenticated user's roles and permissions, returning 401 on an invalid/missing token or unknown user.
- Add `require_permission(permission)` and `require_role(role)` dependency factories that enforce RBAC, returning 403 when the current user lacks the required grant.
- Add read services `RoleService` and `PermissionService` to query the roles and permissions seeded in Fase 4.
- Configure application-wide security: CORS middleware, public auth routes vs. JWT-protected resource routes, and per-endpoint permission requirements (e.g. `CLIENT_CREATE`, `CLIENT_READ`) applied to the existing routers.
- Add the new dependencies to `pyproject.toml` (`python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`).

## Capabilities

### New Capabilities

- `password-hashing`: BCrypt-based password hashing and verification utilities in the shared security module.
- `jwt-tokens`: JWT settings plus a `JwtService` that issues, decodes, validates, and extracts the subject from signed access tokens.
- `authentication`: Credential-based login (`AuthenticationService`, login DTOs, `AuthRouter`) that verifies username/password and returns a JWT together with the user profile.
- `current-user-resolution`: A `get_current_user` dependency and `UserDetails` wrapper that turn a bearer token into the authenticated user with its roles and permissions.
- `rbac-authorization`: `require_permission`/`require_role` dependency factories enforcing permission- and role-based access, rejecting insufficient grants with 403.
- `role-permission-services`: Read services (`RoleService`, `PermissionService`) exposing the roles and permissions defined in Fase 4.
- `endpoint-security`: Application-wide security wiring — CORS, public vs. protected routes, and per-endpoint permission requirements applied to the existing routers.

### Modified Capabilities

None — this phase adds the security layer on top of the Fase 6 API; it introduces new behavior rather than changing previously specified requirements.

## Impact

- **Dependencies**: Adds `python-jose[cryptography]`, `passlib[bcrypt]`, and `python-multipart` to `pyproject.toml`.
- **Consumes**: Auth entities (`User`, `Role`, `Permission`) and their repositories from Fase 3/5, the roles/permissions/admin seed data from Fase 4, the routers from Fase 6, and `energyhub.config.settings`.
- **Provides**: The `get_current_user`, `require_permission`, and `require_role` dependencies plus `JwtService`/`AuthenticationService`, consumed by every protected router.
- **New artifacts**: `shared/infrastructure/security/` (hashing, RBAC dependencies), `auth/infrastructure/security/` (`JwtService`, `UserDetails`, `get_current_user`), `auth/application/dto/` and `application/service/` (login, role, and permission services), and `auth/presentation/router/auth_router.py`.
- **Configuration**: New `secret_key`/`algorithm`/`access_token_expire_minutes` settings; the default `secret_key` and the seeded admin credentials MUST be rotated before any production use.
- **Behavioral change**: Resource endpoints that were open now require a valid JWT and the appropriate permission — unauthenticated calls receive 401 and unauthorized calls 403.
