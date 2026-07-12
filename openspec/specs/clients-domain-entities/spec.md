# clients-domain-entities Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: Client entity creation
The system SHALL create a Client entity in clients/domain/entity/ for client management.

#### Scenario: Client entity structure
- **WHEN** the Client entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have cnpj field
- **THEN** it SHALL have corporate_name field
- **THEN** it SHALL have optional trade_name field
- **THEN** it SHALL have optional email field
- **THEN** it SHALL have optional phone field
- **THEN** it SHALL have optional address field
- **THEN** it SHALL have optional city field
- **THEN** it SHALL have optional state field
- **THEN** it SHALL have optional zip_code field
- **THEN** it SHALL have active field defaulting to True
- **THEN** it SHALL have contacts list with default factory

### Requirement: Contact entity creation
The system SHALL create a Contact entity in clients/domain/entity/ for client contacts.

#### Scenario: Contact entity structure
- **WHEN** the Contact entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have client_id field
- **THEN** it SHALL have	name field
- **THEN** it SHALL have optional email field
- **THEN** it SHALL have optional phone field
- **THEN** it SHALL have optional position field
- **THEN** it SHALL have type field using ContactType enum
- **THEN** it SHALL have optional client reference

