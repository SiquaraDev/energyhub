# domain-enums Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: ContactType enum creation
The system SHALL create ContactType enum in clients/domain/entity/ for contact types.

#### Scenario: ContactType enum values
- **WHEN** ContactType enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have PRIMARY value
- **THEN** it SHALL have BILLING value
- **THEN** it SHALL have TECHNICAL value
- **THEN** it SHALL have COMMERCIAL value

### Requirement: ContractStatus enum creation
The system SHALL create ContractStatus enum in contracts/domain/entity/ for contract states.

#### Scenario: ContractStatus enum values
- **WHEN** ContractStatus enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have DRAFT value
- **THEN** it SHALL have PENDING_APPROVAL value
- **THEN** it SHALL have APPROVED value
- **THEN** it SHALL have ACTIVE value
- **THEN** it SHALL have SUSPENDED value
- **THEN** it SHALL have TERMINATED value
- **THEN** it SHALL have EXPIRED value

### Requirement: ContractType enum creation
The system SHALL create ContractType enum in contracts/domain/entity/ for contract types.

#### Scenario: ContractType enum values
- **WHEN** ContractType enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have PURCHASE value
- **THEN** it SHALL have SALE value
- **THEN** it SHALL have BIDIRECTIONAL value

### Requirement: NegotiationStatus enum creation
The system SHALL create NegotiationStatus enum in negotiations/domain/entity/ for negotiation states.

#### Scenario: NegotiationStatus enum values
- **WHEN** NegotiationStatus enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have DRAFT value
- **THEN** it SHALL have IN_PROGRESS value
- **THEN** it SHALL have COMPLETED value
- **THEN** it SHALL have CANCELLED value

### Requirement: TransactionType enum creation
The system SHALL create TransactionType enum in negotiations/domain/entity/ for transaction types.

#### Scenario: TransactionType enum values
- **WHEN** TransactionType enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have BUY value
- **THEN** it SHALL have SELL value

### Requirement: InvoiceStatus enum creation
The system SHALL create InvoiceStatus enum in financial/domain/entity/ for invoice states.

#### Scenario: InvoiceStatus enum values
- **WHEN** InvoiceStatus enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have DRAFT value
- **THEN** it SHALL have ISSUED value
- **THEN** it SHALL have PAID value
- **THEN** it SHALL have OVERDUE value
- **THEN** it SHALL have CANCELLED value

### Requirement: NotificationStatus enum creation
The system SHALL create NotificationStatus enum in notifications/domain/entity/ for notification states.

#### Scenario: NotificationStatus enum values
- **WHEN** NotificationStatus enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have PENDING value
- **THEN** it SHALL have SENT value
- **THEN** it SHALL have READ value
- **THEN** it SHALL have FAILED value

### Requirement: AuditAction enum creation
The system SHALL create AuditAction enum in audit/domain/entity/ for audit actions.

#### Scenario: AuditAction enum values
- **WHEN** AuditAction enum is created
- **THEN** it SHALL be a string enum
- **THEN** it SHALL have CREATE value
- **THEN** it SHALL have UPDATE value
- **THEN** it SHALL have DELETE value
- **THEN** it SHALL have LOGIN value
- **THEN** it SHALL have LOGOUT value

