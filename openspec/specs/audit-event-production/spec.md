# audit-event-production Specification

## Purpose
TBD - created by archiving change fix-microservices-gaps. Update Purpose after archive.
## Requirements
### Requirement: Audit event producer publishes to the audit queue

The system SHALL provide an `AuditEventProducer` that subclasses the generic `EventProducer` and exposes a typed operation to publish an `AuditEvent` to the configured audit queue (`RabbitMQConfig.AUDIT_QUEUE`), reusing the base producer's robust connection, durable-queue declaration, and persistent delivery so audit messages survive a broker restart.

#### Scenario: Audit event published to the audit queue

- **WHEN** the `AuditEventProducer` is asked to publish an `AuditEvent`
- **THEN** the event is JSON-serialized and published to the `audit` queue via the default exchange with the audit queue name as the routing key

#### Scenario: Audit message published with persistent delivery

- **WHEN** the `AuditEventProducer` publishes any audit event
- **THEN** the message is sent with persistent delivery mode over a robust connection so it is retained across a broker restart

### Requirement: Audit events carry a complete, consumer-compatible payload

Each audit event SHALL be a well-formed `AuditEvent` carrying the actor (`user_id`), the `action`, the `entity_type`, the `entity_id`, a `details` payload, and a `timestamp`, so that the message validates against the shared `AuditEvent` contract consumed by the `audit-service`.

#### Scenario: Payload includes all required fields

- **WHEN** an audit event is produced for a business operation
- **THEN** its payload contains a `user_id`, an `action`, an `entity_type`, an `entity_id`, a `details` object, and a `timestamp`

#### Scenario: Action reflects the operation performed

- **WHEN** a create, update, or delete operation produces its audit event
- **THEN** the event's `action` field identifies the corresponding operation so the recorded trail distinguishes creates, updates, and deletes

#### Scenario: Published payload validates against the consumer contract

- **WHEN** the `audit-service` decodes a message from the audit queue
- **THEN** the payload validates as an `AuditEvent` with no missing or mistyped required fields

### Requirement: Business write operations populate the audit trail end to end

Business write operations across the services SHALL result in a persisted audit record: an audit event emitted by a service is consumed by the existing `AuditConsumer` and stored as an `AuditLog`, so the audit trail reflects real business activity rather than remaining empty.

#### Scenario: A business write results in a persisted audit record

- **WHEN** a service performs a create, update, or delete and emits its audit event, and the broker and `audit-service` are available
- **THEN** the `AuditConsumer` receives the event from the audit queue and persists a matching `AuditLog` entry

#### Scenario: Audit trail is populated rather than starved

- **WHEN** business write operations occur across the services over time
- **THEN** corresponding audit records accumulate in the audit store, because the audit queue now has a producer feeding the existing consumer

