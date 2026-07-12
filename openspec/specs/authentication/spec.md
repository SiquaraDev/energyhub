# authentication Specification

## Purpose
TBD - created by archiving change implement-fase-7. Update Purpose after archive.
## Requirements
### Requirement: Login request and response contracts

The system SHALL define `LoginRequestDTO` (username, password) and `LoginResponseDTO` (access token, token type, user profile) as Pydantic models in `auth/application/dto/`.

#### Scenario: Login response shape

- **WHEN** a login succeeds
- **THEN** the response contains `access_token`, `token_type` defaulting to `"bearer"`, and the authenticated `user` profile

### Requirement: Credential-based authentication

`AuthenticationService.login` SHALL look up the user by username, verify the supplied password against the stored hash, and issue a JWT for the authenticated subject.

#### Scenario: Successful login issues a token

- **WHEN** `login` is called with a valid username and matching password
- **THEN** a JWT is created for the user and returned in a `LoginResponseDTO` together with the user profile

#### Scenario: Wrong password is rejected

- **WHEN** `login` is called with a known username but an incorrect password
- **THEN** an invalid-credentials error is raised and no token is issued

### Requirement: Unknown and inactive users are rejected

`AuthenticationService.login` SHALL reject authentication when no user matches the username or when the matched user is inactive, without revealing which condition failed.

#### Scenario: Unknown username

- **WHEN** `login` is called with a username that does not exist
- **THEN** an invalid-credentials error is raised

#### Scenario: Inactive account

- **WHEN** `login` is called with valid credentials for a user whose account is inactive
- **THEN** authentication is refused and no token is issued

### Requirement: Login endpoint

`AuthRouter` SHALL expose `POST /api/v1/auth/login` that accepts a `LoginRequestDTO` and returns a `LoginResponseDTO`.

#### Scenario: Posting valid credentials

- **WHEN** a client POSTs valid credentials to `/api/v1/auth/login`
- **THEN** the endpoint returns 200 with the access token and user profile

#### Scenario: Posting invalid credentials

- **WHEN** a client POSTs invalid credentials to `/api/v1/auth/login`
- **THEN** the endpoint returns an authentication error status and no token

