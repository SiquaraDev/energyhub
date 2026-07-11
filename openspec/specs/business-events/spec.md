# business-events Specification

## Purpose
TBD - created by archiving change implement-fase-0. Update Purpose after archive.
## Requirements
### Requirement: Business event identification
The system SHALL identify all important business events that occur in the EnergyHub platform.

#### Scenario: Event completeness
- **WHEN** identifying business events
- **THEN** the list SHALL include User created event
- **THEN** the list SHALL include User updated event
- **THEN** the list SHALL include User deleted event
- **THEN** the list SHALL include Client created event
- **THEN** the list SHALL include Client updated event
- **THEN** the list SHALL include Contract created event
- **THEN** the list SHALL include Contract approved event
- **THEN** the list SHALL include Contract rejected event
- **THEN** the list SHALL include Negotiation initiated event
- **THEN** the list SHALL include Negotiation completed event
- **THEN** the list SHALL include Negotiation cancelled event
- **THEN** the list SHALL include Energy bought event
- **THEN** the list SHALL include Energy sold event
- **THEN** the list SHALL include Invoice issued event
- **THEN** the list SHALL include Invoice paid event
- **THEN** the list SHALL include Invoice cancelled event
- **THEN** the list SHALL include Notification sent event
- **THEN** the list SHALL include Report generated event

### Requirement: Event definition
The system SHALL define for each business event its name, payload, trigger condition, and consuming systems.

#### Scenario: Event specification
- **WHEN** defining business events
- **THEN** each event SHALL have a unique name
- **THEN** each event SHALL have a defined payload structure
- **THEN** each event SHALL specify when it is triggered
- **THEN** each event SHALL identify which systems should consume it

