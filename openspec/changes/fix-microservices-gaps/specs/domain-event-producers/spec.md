## MODIFIED Requirements

### Requirement: Producer integration in application services

Application services SHALL publish the corresponding domain event only after the primary state change has succeeded, so that a create, update, or delete emits its event once persisted. In addition to the domain event, each successful create, update, or delete SHALL emit an audit event to the audit queue as a non-blocking side-effect after persistence, so that the persisted write remains the source of truth and a broker outage cannot roll it back.

#### Scenario: Event emitted after successful create

- **WHEN** a service `create` operation persists a new entity successfully
- **THEN** the service publishes the created event carrying the response DTO after persistence completes

#### Scenario: Delete emits a deletion event

- **WHEN** a service `delete` operation removes an entity successfully
- **THEN** the service publishes a deletion event carrying the entity identifier

#### Scenario: Audit event emitted after a successful write

- **WHEN** a service create, update, or delete operation persists its change successfully
- **THEN** the service also emits an audit event to the audit queue after persistence, carrying the actor, the action, and the affected entity's type and identifier

#### Scenario: Audit publication failure does not roll back the write

- **WHEN** the audit event fails to publish because the broker is unavailable
- **THEN** the failure is logged and swallowed, the persisted write is preserved, and the business operation still completes successfully
