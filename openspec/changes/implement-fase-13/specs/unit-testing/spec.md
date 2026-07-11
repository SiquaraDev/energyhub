## ADDED Requirements

### Requirement: Service unit tests with isolated collaborators

The suite SHALL provide unit tests for application-layer services (starting with `UserService` and `ClientService`) that construct the service with mocked collaborators (repositories, mappers, and other services) so each test exercises only the service logic without touching real infrastructure.

#### Scenario: Service under test uses mocked dependencies

- **WHEN** a service unit test instantiates the service
- **THEN** its repository, mapper, and external-service collaborators are test doubles (`Mock`/`AsyncMock`), and no database, broker, or network call is made

### Requirement: Happy-path coverage

Service unit tests SHALL cover the successful path of each primary operation and assert both the returned value and the key collaborator interactions.

#### Scenario: Creating a user succeeds when data is valid

- **WHEN** `UserService.create` is called with a valid request and the username and email do not already exist
- **THEN** a response is returned reflecting the created user and the repository `save` is invoked exactly once

### Requirement: Domain-exception path coverage

Service unit tests SHALL cover the failure paths where domain rules are violated, asserting that the expected domain exception is raised and that no persisting side effect occurs.

#### Scenario: Creating a user fails when the username already exists

- **WHEN** `UserService.create` is called and the username already exists
- **THEN** a `UserAlreadyExistsException` is raised and the repository `save` is not called

#### Scenario: Creating a client fails when the CNPJ already exists

- **WHEN** `ClientService.create` is called and the CNPJ already exists
- **THEN** a `ClientAlreadyExistsException` is raised and the repository `save` is not called

### Requirement: Consistent test naming

Unit tests SHALL follow a behavior-describing naming convention (`test_should_<expected>_when_<condition>`) so intent is readable from the test report.

#### Scenario: Test names describe behavior

- **WHEN** the test report lists the service unit tests
- **THEN** each name states the expected outcome and the triggering condition rather than an implementation detail
