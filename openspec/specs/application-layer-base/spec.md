# application-layer-base Specification

## Purpose
TBD - created by archiving change implement-fase-2. Update Purpose after archive.
## Requirements
### Requirement: BaseDTO class
The system SHALL create a BaseDTO class in shared/application/dto/ with common DTO fields.

#### Scenario: BaseDTO creation
- **WHEN** the application layer is created
- **THEN** the system SHALL create BaseDTO as a dataclass
- **THEN** BaseDTO SHALL have an optional id field
- **THEN** BaseDTO SHALL have an optional created_at field
- **THEN** BaseDTO SHALL have an optional updated_at field

### Requirement: UseCase interface
The system SHALL create a UseCase interface in shared/application/usecase/ with generic execute method.

#### Scenario: UseCase interface creation
- **WHEN** the application layer is created
- **THEN** the system SHALL create UseCase as an abstract base class
- **THEN** UseCase SHALL be generic with type parameters Input and Output
- **THEN** UseCase SHALL define an abstract execute method accepting Input and returning Output

### Requirement: ApplicationException class
The system SHALL create an ApplicationException base class in shared/application/exception/.

#### Scenario: ApplicationException creation
- **WHEN** the application layer is created
- **THEN** the system SHALL create ApplicationException extending Exception
- **THEN** ApplicationException SHALL accept a message parameter
- **THEN** ApplicationException SHALL store the message as an attribute
- **THEN** ApplicationException SHALL implement __str__ returning the message

