## ADDED Requirements

### Requirement: Entity identification
The system SHALL identify all main entities required for the EnergyHub database.

#### Scenario: Entity completeness
- **WHEN** designing the database schema
- **THEN** the design SHALL include User entity
- **THEN** the design SHALL include Role entity
- **THEN** the design SHALL include Permission entity
- **THEN** the design SHALL include Client entity
- **THEN** the design SHALL include Contract entity
- **THEN** the design SHALL include Negotiation entity
- **THEN** the design SHALL include EnergyTransaction entity
- **THEN** the design SHALL include Invoice entity
- **THEN** the design SHALL include AuditLog entity
- **THEN** the design SHALL include Notification entity
- **THEN** the design SHALL include Report entity

### Requirement: Entity attributes definition
The system SHALL define all attributes for each entity including data types and constraints.

#### Scenario: Attribute specification
- **WHEN** defining entity attributes
- **THEN** each entity SHALL list all required fields
- **THEN** each field SHALL have a defined data type
- **THEN** each field SHALL have defined constraints (NOT NULL, UNIQUE, etc.)

### Requirement: Relationship definition
The system SHALL define all relationships between entities with their cardinality.

#### Scenario: Relationship modeling
- **WHEN** defining entity relationships
- **THEN** User and Role SHALL have Many-to-Many relationship
- **THEN** Role and Permission SHALL have Many-to-Many relationship
- **THEN** Client and Contract SHALL have One-to-Many relationship
- **THEN** Contract and Negotiation SHALL have One-to-Many relationship
- **THEN** Negotiation and EnergyTransaction SHALL have One-to-Many relationship
- **THEN** Client and Invoice SHALL have One-to-Many relationship
- **THEN** User and AuditLog SHALL have One-to-Many relationship
- **THEN** User and Notification SHALL have One-to-Many relationship

### Requirement: DER diagram creation
The system SHALL have a complete Entity-Relationship diagram created using diagramming tools.

#### Scenario: DER diagram visualization
- **WHEN** entity relationships are defined
- **THEN** a DER diagram SHALL be created using Mermaid, Draw.io, or similar tools
- **THEN** the diagram SHALL show all entities with their attributes
- **THEN** the diagram SHALL show all relationships with cardinality
- **THEN** the diagram SHALL be included in the documentation
