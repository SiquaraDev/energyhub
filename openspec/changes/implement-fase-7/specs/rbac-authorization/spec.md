## ADDED Requirements

### Requirement: Permission-based access guard

The system SHALL provide a `require_permission(permission)` dependency factory that resolves the current user via `get_current_user` and allows the request only when the user holds the named permission.

#### Scenario: User has the required permission

- **WHEN** a request reaches an endpoint guarded by `require_permission("CLIENT_CREATE")` and the current user's permissions include `CLIENT_CREATE`
- **THEN** the request proceeds and the current user is returned to the handler

#### Scenario: User lacks the required permission

- **WHEN** a request reaches an endpoint guarded by `require_permission("CLIENT_CREATE")` and the current user does not hold `CLIENT_CREATE`
- **THEN** the guard raises HTTP 403 identifying the required permission

### Requirement: Role-based access guard

The system SHALL provide a `require_role(role)` dependency factory that allows the request only when the current user holds the named role.

#### Scenario: User has the required role

- **WHEN** a request reaches an endpoint guarded by `require_role("ADMIN")` and the current user's roles include `ADMIN`
- **THEN** the request proceeds

#### Scenario: User lacks the required role

- **WHEN** a request reaches an endpoint guarded by `require_role("ADMIN")` and the current user does not hold `ADMIN`
- **THEN** the guard raises HTTP 403 identifying the required role

### Requirement: Authorization runs after authentication

The RBAC guards SHALL depend on `get_current_user`, so an unauthenticated request is rejected with 401 before any permission or role check runs.

#### Scenario: Unauthenticated request to a guarded endpoint

- **WHEN** a request without a valid token reaches an endpoint guarded by `require_permission` or `require_role`
- **THEN** it is rejected with HTTP 401 and the permission/role check is not evaluated
