## ADDED Requirements

### Requirement: Notification consumer subscriptions

The system SHALL provide a `NotificationConsumer` that subscribes to the user-created, client-created, contract-approved, and invoice-issued queues and handles each event to drive downstream notifications.

#### Scenario: Consumer binds all notification handlers on start

- **WHEN** `NotificationConsumer.start_consuming()` runs
- **THEN** it declares the durable notification-relevant queues and registers a handler for each of the user-created, client-created, contract-approved, and invoice-issued events

#### Scenario: Handler decodes the event payload

- **WHEN** a message arrives on a subscribed queue
- **THEN** the handler decodes the JSON body into the event data and processes it (for example logging and triggering the relevant notification action)

### Requirement: Audit consumer persistence

The system SHALL provide an `AuditConsumer` that consumes the audit queue and persists an audit log entry for each received event using the audit log repository.

#### Scenario: Audit event stored

- **WHEN** the `AuditConsumer` receives a message on the audit queue
- **THEN** it constructs an `AuditLog` from the event fields (user, action, entity type, entity id, details, timestamp) and saves it via the `AuditLogRepository`

### Requirement: Audit event schema

The system SHALL define an `AuditEvent` model carrying `user_id`, `action`, `entity_type`, `entity_id`, and `details`, providing a typed contract for messages published to the audit queue.

#### Scenario: Well-formed audit event validates

- **WHEN** an `AuditEvent` is constructed with all required fields
- **THEN** validation succeeds and the model can be serialized for publication to the audit queue

### Requirement: Bounded prefetch consumption

Consumers SHALL set a bounded prefetch (`prefetch_count=1`) so a worker fetches only one unacknowledged message at a time, distributing load evenly and preventing a single consumer from buffering the queue.

#### Scenario: Consumer limits in-flight messages

- **WHEN** a consumer channel is opened for consumption
- **THEN** its QoS is configured so at most one unacknowledged message is delivered to that consumer before the previous one is acknowledged
