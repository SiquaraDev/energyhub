# financial-domain-entities Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: Invoice entity creation
The system SHALL create an Invoice entity in financial/domain/entity/ for billing.

#### Scenario: Invoice entity structure
- **WHEN** the Invoice entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have invoice_number field
- **THEN** it SHALL have client_id field
- **THEN** it SHALL have amount field using Decimal
- **THEN** it SHALL have due_date field
- **THEN** it SHALL have status field using InvoiceStatus enum
- **THEN** it SHALL have optional client reference

### Requirement: Payment entity creation
The system SHALL create a Payment entity in financial/domain/entity/ for payment tracking.

#### Scenario: Payment entity structure
- **WHEN** the Payment entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have invoice_id field
- **THEN** it SHALL have amount field using Decimal
- **THEN** it SHALL have payment_date field
- **THEN** it SHALL have optional invoice reference

