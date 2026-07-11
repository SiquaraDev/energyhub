## ADDED Requirements

### Requirement: Pydantic field validators
The system SHALL implement Pydantic field validators for entity fields.

#### Scenario: Username validation
- **WHEN** User entity username field is set
- **THEN** it SHALL validate username is not empty
- **THEN** it SHALL raise ValueError if username is empty

#### Scenario: Email validation
- **WHEN** User entity email field is set
- **THEN** it SHALL validate email contains @ symbol
- **THEN** it SHALL raise ValueError if email is invalid

### Requirement: Business rule exceptions
The system SHALL create specific domain exceptions for business rule violations.

#### Scenario: InvalidContractStatusException
- **WHEN** InvalidContractStatusException is created
- **THEN** it SHALL extend DomainException
- **THEN** it SHALL accept a message parameter

#### Scenario: InvalidClientStateException
- **WHEN** InvalidClientStateException is created
- **THEN** it SHALL extend DomainException
- **THEN** it SHALL accept a message parameter

#### Scenario: InvalidNegotiationException
- **WHEN** InvalidNegotiationException is created
- **THEN** it SHALL extend DomainException
- **THEN** it SHALL accept a message parameter

### Requirement: Entity relationship helper methods
The system SHALL implement helper methods in entities for relationship management.

#### Scenario: Role management methods
- **WHEN** User entity add_role method is called
- **THEN** it SHALL add role to user's roles list
- **THEN** it SHALL add user to role's users list

#### Scenario: Role removal methods
- **WHEN** User entity remove_role method is called
- **THEN** it SHALL remove role from user's roles list
- **THEN** it SHALL remove user from role's users list
