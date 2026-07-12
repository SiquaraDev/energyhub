# jwt-tokens Specification

## Purpose
TBD - created by archiving change implement-fase-7. Update Purpose after archive.
## Requirements
### Requirement: JWT security settings

The system SHALL define `secret_key`, `algorithm`, and `access_token_expire_minutes` in `energyhub.config.settings`, and `JwtService` MUST read its signing configuration from those settings.

#### Scenario: Service is configured from settings

- **WHEN** `JwtService` is constructed
- **THEN** it uses `settings.secret_key`, `settings.algorithm`, and `settings.access_token_expire_minutes` to sign and expire tokens

### Requirement: Signed access token creation

`JwtService` SHALL provide `create_token` that issues a signed JWT containing the subject (`sub`), an expiration (`exp`) derived from `access_token_expire_minutes`, and any additional claims supplied by the caller.

#### Scenario: Token carries subject and expiration

- **WHEN** `create_token` is called with a subject
- **THEN** the returned token is signed with the configured secret and algorithm and encodes the `sub` and an `exp` claim in the future

#### Scenario: Additional claims are embedded

- **WHEN** `create_token` is called with extra claims
- **THEN** those claims are included in the encoded token payload alongside `sub` and `exp`

### Requirement: Token decoding and validation

`JwtService` SHALL provide `decode_token`, `extract_username`, and `is_token_valid` that verify the signature and expiration, returning the payload/subject on success and a null/false result on failure.

#### Scenario: Decoding a valid token

- **WHEN** `decode_token` is called with a token signed by this service and not yet expired
- **THEN** the decoded payload is returned

#### Scenario: Decoding a tampered or malformed token

- **WHEN** `decode_token` is called with a token whose signature is invalid or that is malformed
- **THEN** `None` is returned rather than raising to the caller

#### Scenario: Extracting the subject

- **WHEN** `extract_username` is called with a valid token
- **THEN** the value of the `sub` claim is returned, and `None` is returned when the token is invalid

#### Scenario: Expired token is not valid

- **WHEN** `is_token_valid` is called with a token whose `exp` is in the past
- **THEN** it returns `False`

