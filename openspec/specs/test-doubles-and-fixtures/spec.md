# test-doubles-and-fixtures Specification

## Purpose
TBD - created by archiving change implement-fase-13. Update Purpose after archive.
## Requirements
### Requirement: Shared fixtures for external dependencies

The suite SHALL provide reusable fixtures in `tests/conftest.py` that return test doubles for external dependencies (`email_service`, `notification_service`, `event_producer`) so any test can inject them without redefining the mocks.

#### Scenario: A test injects a shared external-service double

- **WHEN** a test requests the `email_service` fixture
- **THEN** it receives an `AsyncMock` standing in for the real email service, shared through `conftest.py` rather than declared inline

### Requirement: Async-aware test doubles

Doubles for asynchronous collaborators SHALL be awaitable (`AsyncMock`), and doubles for synchronous collaborators SHALL be plain `Mock`, so awaiting a mocked async call does not raise.

#### Scenario: Awaiting a mocked async call resolves

- **WHEN** a service under test awaits a method on an `AsyncMock` collaborator
- **THEN** the call resolves to the configured return value without raising a "coroutine was never awaited" or "cannot await Mock" error

### Requirement: Interaction assertions on doubles

Tests SHALL be able to assert that side-effecting external calls happened (or did not happen) through the shared doubles.

#### Scenario: Welcome email is sent on client creation

- **WHEN** a client is created and the flow uses the `email_service` double
- **THEN** the test can assert `send_welcome_email` was called exactly once

#### Scenario: No external call on a rejected operation

- **WHEN** an operation is rejected by a domain rule
- **THEN** the test can assert the external-service doubles were not called

