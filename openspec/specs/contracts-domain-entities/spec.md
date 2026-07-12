# contracts-domain-entities Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: Contract entity creation
The system SHALL create a Contract entity in contracts/domain/entity/ for energy contracts.

#### Scenario: Contract entity structure
- **WHEN** the Contract entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have contract_number field
- **THEN** it SHALL have client_id field
- **THEN** it SHALL have start_date field
- **THEN** it SHALL have end_date field
- **THEN** it SHALL have energy_amount field using Decimal
- **THEN** it SHALL have unit_price field using Decimal
- **THEN** it SHALL have total_value field using Decimal
- **THEN** it SHALL have status field using ContractStatus enum
- **THEN** it SHALL have type field using ContractType enum
- **THEN** it SHALL have optional client reference

### Requirement: Contract business methods
The system SHALL implement business methods in Contract entity for state transitions.

#### Scenario: Contract approval
- **WHEN** approve method is called on a contract
- **THEN** it SHALL validate status is PENDING_APPROVAL
- **THEN** it SHALL raise DomainException if status is invalid
- **THEN** it SHALL set status to APPROVED

#### Scenario: Contract activation
- **WHEN** activate method is called on a contract
- **THEN** it SHALL validate status is APPROVED
- **THEN** it SHALL validate start_date is not in the future
- **THEN** it SHALL raise DomainException if validations fail
- **THEN** it SHALL set status to ACTIVE

