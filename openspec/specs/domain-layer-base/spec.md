# domain-layer-base Specification

## Purpose
TBD - created by archiving change implement-fase-2. Update Purpose after archive.
## Requirements
### Requirement: BaseEntity class
The system SHALL create a BaseEntity class in shared/domain/entity/ with common entity fields.

#### Scenario: BaseEntity creation
- **WHEN** the domain layer is created
- **THEN** the system SHALL create BaseEntity as a dataclass
- **THEN** BaseEntity SHALL have an id field with default factory generating UUID
- **THEN** BaseEntity SHALL have a created_at field with default factory generating current UTC datetime
- **THEN** BaseEntity SHALL have an updated_at field with default factory generating current UTC datetime
- **THEN** BaseEntity SHALL have a __post_init__ method to initialize fields if None
- **THEN** BaseEntity SHALL have an update_timestamp method to update updated_at field

### Requirement: Repository interface
The system SHALL create a Repository interface in shared/domain/repository/ with generic CRUD operations.

#### Scenario: Repository interface creation
- **WHEN** the domain layer is created
- **THEN** the system SHALL create Repository as an abstract base class
- **THEN** Repository SHALL be generic with type parameters T (entity) and ID (identifier)
- **THEN** Repository SHALL define an abstract save method
- **THEN** Repository SHALL define an abstract find_by_id method
- **THEN** Repository SHALL define an abstract find_all method
- **THEN** Repository SHALL define an abstract delete_by_id method
- **THEN** Repository SHALL define an abstract exists_by_id method

### Requirement: DomainException class
The system SHALL create a DomainException base class in shared/domain/exception/.

#### Scenario: DomainException creation
- **WHEN** the domain layer is created
- **THEN** the system SHALL create DomainException extending Exception
- **THEN** DomainException SHALL accept a message parameter
- **THEN** DomainException SHALL store the message as an attribute
- **THEN** DomainException SHALL implement __str__ returning the message

### Requirement: Specific domain exceptions
The system SHALL create specific domain exception classes.

#### Scenario: Specific exceptions creation
- **WHEN** the domain layer is created
- **THEN** the system SHALL create ResourceNotFoundException extending DomainException
- **THEN** the system SHALL create ValidationException extending DomainException
- **THEN** the system SHALL create BusinessRuleException extending DomainException

