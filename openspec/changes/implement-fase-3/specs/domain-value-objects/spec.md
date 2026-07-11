## ADDED Requirements

### Requirement: CNPJ Value Object creation
The system SHALL create CNPJ Value Object in shared/domain/valueobject/ for CNPJ validation.

#### Scenario: CNPJ validation
- **WHEN** CNPJ Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL validate CNPJ format in __post_init__
- **THEN** it SHALL raise ValueError if CNPJ is invalid
- **THEN** it SHALL format CNPJ to standard format

### Requirement: Email Value Object creation
The system SHALL create Email Value Object in shared/domain/valueobject/ for email validation.

#### Scenario: Email validation
- **WHEN** Email Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL validate email format in __post_init__
- **THEN** it SHALL raise ValueError if email is invalid
- **THEN** it SHALL convert email to lowercase

### Requirement: Money Value Object creation
The system SHALL create Money Value Object in shared/domain/valueobject/ for monetary values.

#### Scenario: Money Value Object
- **WHEN** Money Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL have amount field using Decimal
- **THEN** it SHALL have currency field

### Requirement: PhoneNumber Value Object creation
The system SHALL create PhoneNumber Value Object in shared/domain/valueobject/ for phone validation.

#### Scenario: PhoneNumber validation
- **WHEN** PhoneNumber Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL validate phone format in __post_init__
- **THEN** it SHALL raise ValueError if phone is invalid

### Requirement: Address Value Object creation
The system SHALL create Address Value Object in shared/domain/valueobject/ for address representation.

#### Scenario: Address Value Object
- **WHEN** Address Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL have street field
- **THEN** it SHALL have city field
- **THEN** it SHALL have state field
- **THEN** it SHALL have zip_code field
- **THEN** it SHALL have country field

### Requirement: Percentage Value Object creation
The system SHALL create Percentage Value Object in shared/domain/valueobject/ for percentage values.

#### Scenario: Percentage Value Object
- **WHEN** Percentage Value Object is created
- **THEN** it SHALL be a frozen dataclass
- **THEN** it SHALL have value field using Decimal
- **THEN** it SHALL validate value is between 0 and 100
