## ADDED Requirements

### Requirement: BCrypt password hashing utilities

The system SHALL provide a shared security module in `shared/infrastructure/security/` exposing `get_password_hash` and `verify_password` backed by a BCrypt `passlib` `CryptContext`.

#### Scenario: Hashing a plaintext password

- **WHEN** `get_password_hash` is called with a plaintext password
- **THEN** it returns a BCrypt hash that is not equal to the plaintext and encodes the algorithm and salt

#### Scenario: Verifying a correct password

- **WHEN** `verify_password` is called with a plaintext password and its matching hash
- **THEN** it returns `True`

#### Scenario: Rejecting an incorrect password

- **WHEN** `verify_password` is called with a plaintext password that does not match the stored hash
- **THEN** it returns `False`

### Requirement: Passwords are never stored or compared in plaintext

The system SHALL persist and compare user passwords only through the hashing utilities; plaintext passwords MUST never be stored or logged.

#### Scenario: Stored credential is a hash

- **WHEN** a user credential is persisted
- **THEN** the stored value is the BCrypt hash produced by `get_password_hash`, never the raw password
