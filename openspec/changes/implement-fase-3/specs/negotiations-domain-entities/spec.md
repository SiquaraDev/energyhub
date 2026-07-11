## ADDED Requirements

### Requirement: Negotiation entity creation
The system SHALL create a Negotiation entity in negotiations/domain/entity/ for energy negotiations.

#### Scenario: Negotiation entity structure
- **WHEN** the Negotiation entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have contract_id field
- **THEN** it SHALL have status field using NegotiationStatus enum
- **THEN** it SHALL have optional contract reference

### Requirement: EnergyTransaction entity creation
The system SHALL create an EnergyTransaction entity in negotiations/domain/entity/ for energy transactions.

#### Scenario: EnergyTransaction entity structure
- **WHEN** the EnergyTransaction entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have negotiation_id field
- **THEN** it SHALL have amount field using Decimal
- **THEN** it SHALL have price field using Decimal
- **THEN** it SHALL have type field using TransactionType enum
- **THEN** it SHALL have transaction_date field
- **THEN** it SHALL have optional negotiation reference
