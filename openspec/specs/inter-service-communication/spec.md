# inter-service-communication Specification

## Purpose
TBD - created by archiving change implement-fase-15. Update Purpose after archive.
## Requirements
### Requirement: Cross-service calls use dedicated HTTP clients

The system SHALL provide a dedicated async HTTP client per upstream dependency (for example `AuthClient`, `ClientClient`, `ContractClient`) built on `httpx`, exposing typed methods for the operations a service needs from another context.

#### Scenario: Client exposes the needed operations

- **WHEN** a service must fetch a user from the Auth context
- **THEN** it calls a method such as `AuthClient.get_user_by_id` rather than issuing an ad-hoc request or importing the other service's code

### Requirement: HTTP clients replace former in-process module calls

Every call that a module previously made directly to another module SHALL be replaced by a call through the corresponding HTTP client, preserving the declared dependency direction between contexts.

#### Scenario: In-process dependency becomes a network call

- **WHEN** the Contracts service needs client data that once came from an in-process Clients call
- **THEN** it obtains that data through `ClientClient` over HTTP instead of an in-process import

#### Scenario: Dependency direction is preserved

- **WHEN** a service's HTTP clients are inspected
- **THEN** it holds clients only for the contexts declared upstream of it and none for downstream contexts

### Requirement: Clients surface upstream failures explicitly

Each HTTP client SHALL raise for unsuccessful HTTP responses (for example via `raise_for_status`) so that upstream errors are handled deliberately by the caller rather than silently returning malformed data.

#### Scenario: Non-success response raises

- **WHEN** an upstream service returns an error status to a client call
- **THEN** the client raises an error that the caller can catch, instead of returning the error body as if it were valid data

### Requirement: Clients release their connections

Each HTTP client SHALL expose a way to close its underlying connection pool so service shutdown does not leak connections.

#### Scenario: Client is closed on shutdown

- **WHEN** a service shuts down
- **THEN** each HTTP client's `close` is invoked and its `httpx` connection pool is released

