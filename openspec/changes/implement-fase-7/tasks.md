## 1. Dependencies and Configuration

- [ ] 1.1 Add `python-jose[cryptography]`, `passlib[bcrypt]`, and `python-multipart` to `pyproject.toml` and run `poetry add` to install them
- [ ] 1.2 Add `secret_key`, `algorithm` (default `HS256`), and `access_token_expire_minutes` (default `30`) to `energyhub.config.settings`
- [ ] 1.3 Confirm the app still imports cleanly (`poetry run python -c "import energyhub.config"`)

## 2. Password Hashing

- [ ] 2.1 Create `shared/infrastructure/security/` with a BCrypt `CryptContext` and `get_password_hash`
- [ ] 2.2 Add `verify_password` that checks a plaintext password against a stored hash
- [ ] 2.3 Verify a hash/verify round-trip returns `True` for the correct password and `False` otherwise

## 3. JWT Token Service

- [ ] 3.1 Create `JwtService` in `auth/infrastructure/security/` reading `secret_key`/`algorithm`/`access_token_expire_minutes` from settings
- [ ] 3.2 Implement `create_token(subject, claims)` embedding `sub`, `exp`, and any extra claims
- [ ] 3.3 Implement `decode_token` returning the payload or `None` on invalid/malformed tokens
- [ ] 3.4 Implement `extract_username` and `is_token_valid` (expiration check)

## 4. Login Flow

- [ ] 4.1 Create `LoginRequestDTO` (username, password) in `auth/application/dto/`
- [ ] 4.2 Create `LoginResponseDTO` (access token, `token_type="bearer"`, user profile) in `auth/application/dto/`
- [ ] 4.3 Create `AuthenticationService.login` that finds the user by username and verifies the password with `verify_password`
- [ ] 4.4 Reject unknown users, wrong passwords, and inactive accounts with an invalid-credentials error
- [ ] 4.5 On success, issue a token via `JwtService` and return a `LoginResponseDTO` with the mapped user profile
- [ ] 4.6 Create `AuthRouter` exposing `POST /login` and register it under `/api/v1/auth`

## 5. Current User Resolution

- [ ] 5.1 Create `UserDetails` in `auth/infrastructure/security/` exposing `username`, `active`, `roles`, and flattened `permissions`
- [ ] 5.2 Create the `get_current_user` dependency using `HTTPBearer` and `JwtService.extract_username`
- [ ] 5.3 Raise HTTP 401 (with `WWW-Authenticate: Bearer`) when the token is missing/invalid or the subject matches no user
- [ ] 5.4 Return a `UserDetails` wrapping the loaded user on success

## 6. RBAC Authorization

- [ ] 6.1 Create `require_permission(permission)` in `shared/infrastructure/security/` depending on `get_current_user`
- [ ] 6.2 Raise HTTP 403 when the current user lacks the required permission
- [ ] 6.3 Create `require_role(role)` that raises HTTP 403 when the current user lacks the required role
- [ ] 6.4 Confirm the guards return the current user to the handler when the check passes

## 7. Role and Permission Services

- [ ] 7.1 Create `RoleService` in `auth/application/service/` with `find_all` and `find_by_name` (raising resource-not-found for unknown names)
- [ ] 7.2 Create `PermissionService` with `find_all` and `find_by_role_name`

## 8. Endpoint Security Wiring

- [ ] 8.1 Register CORS middleware on the FastAPI app in `energyhub/main.py`
- [ ] 8.2 Register `/api/v1/auth` as a public route group (no auth dependency)
- [ ] 8.3 Protect the resource routers (clients, contracts, others) with `Depends(get_current_user)`
- [ ] 8.4 Attach per-endpoint `require_permission` guards mapping CRUD actions to permissions (e.g. `CLIENT_CREATE`, `CLIENT_READ`, `CLIENT_UPDATE`, `CLIENT_DELETE`)

## 9. Validation

- [ ] 9.1 Start the app and log in via `POST /api/v1/auth/login` with the seeded admin credentials, confirming a token is returned
- [ ] 9.2 Call a protected endpoint without a token and confirm HTTP 401
- [ ] 9.3 Call a protected endpoint with a valid token but missing permission and confirm HTTP 403
- [ ] 9.4 Call a protected endpoint with a valid token and sufficient permission and confirm HTTP 200
- [ ] 9.5 Run `openspec validate implement-fase-7` and confirm the change is valid
