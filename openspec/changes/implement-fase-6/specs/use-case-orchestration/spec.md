## ADDED Requirements

### Requirement: Use cases implement the shared contract

The system SHALL provide use cases in each module's `application/usecase/` that extend the shared `UseCase[Input, Output]` contract and expose a single async `execute(input_data)` method for one business operation (e.g. `CreateUserUseCase`, `CreateClientUseCase`).

#### Scenario: Use case exposes execute

- **WHEN** a use case extends `UseCase[Input, Output]`
- **THEN** it implements `execute(input_data)` typed to the declared input and output DTOs

### Requirement: Use cases orchestrate services

Use cases SHALL delegate the actual work to application services and MUST NOT embed persistence or mapping logic themselves, so orchestration is separated from business logic.

#### Scenario: Use case delegates to a service

- **WHEN** `execute` is called on a use case with an input DTO
- **THEN** the use case invokes the corresponding service operation and returns its result unchanged

#### Scenario: Domain exceptions propagate

- **WHEN** the delegated service raises a domain exception
- **THEN** the use case propagates it to its caller without swallowing or reclassifying it
