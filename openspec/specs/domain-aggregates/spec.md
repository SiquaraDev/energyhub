# domain-aggregates Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: AuthAggregate creation
The system SHALL create AuthAggregate in auth/domain/ with User as aggregate root.

#### Scenario: AuthAggregate structure
- **WHEN** AuthAggregate is created
- **THEN** it SHALL contain User as aggregate root
- **THEN** it SHALL provide methods to manage roles
- **THEN** it SHALL enforce consistency rules for user-role relationships

### Requirement: ClientAggregate creation
The system SHALL create ClientAggregate in clients/domain/ with Client as aggregate root.

#### Scenario: ClientAggregate structure
- **WHEN** ClientAggregate is created
- **THEN** it SHALL contain Client as aggregate root
- **THEN** it SHALL provide add_contact method
- **THEN** it SHALL provide remove_contact method
- **THEN** it SHALL provide activate method
- **THEN** it SHALL provide deactivate method
- **THEN** it SHALL provide get_client method

### Requirement: ContractAggregate creation
The system SHALL create ContractAggregate in contracts/domain/ with Contract as aggregate root.

#### Scenario: ContractAggregate structure
- **WHEN** ContractAggregate is created
- **THEN** it SHALL contain Contract as aggregate root
- **THEN** it SHALL enforce business rules for contract state transitions

### Requirement: NegotiationAggregate creation
The system SHALL create NegotiationAggregate in negotiations/domain/ with Negotiation as aggregate root.

#### Scenario: NegotiationAggregate structure
- **WHEN** NegotiationAggregate is created
- **THEN** it SHALL contain Negotiation as aggregate root
- **THEN** it SHALL manage EnergyTransaction entities
- **THEN** it SHALL enforce consistency rules for negotiations

### Requirement: FinancialAggregate creation
The system SHALL create FinancialAggregate in financial/domain/ with Invoice as aggregate root.

#### Scenario: FinancialAggregate structure
- **WHEN** FinancialAggregate is created
- **THEN** it SHALL contain Invoice as aggregate root
- **THEN** it SHALL manage Payment entities
- **THEN** it SHALL enforce business rules for invoice-payment relationships

