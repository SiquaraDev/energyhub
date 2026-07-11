## ADDED Requirements

### Requirement: Generic event producer base

The system SHALL provide a generic `EventProducer` base class that manages a robust broker connection and channel and exposes an async `publish(queue, message)` operation used by all concrete producers.

#### Scenario: Connection established lazily before publishing

- **WHEN** `publish` is called on a producer whose channel is not yet open
- **THEN** the producer establishes a robust connection and channel before sending the message

#### Scenario: Message serialized and routed to the queue

- **WHEN** `publish` is called with a queue name and a `dict` payload
- **THEN** the payload is JSON-encoded and published to the default exchange with the queue name as the routing key

### Requirement: Persistent message delivery

The producer SHALL publish messages with persistent delivery mode so that enqueued messages survive a broker restart.

#### Scenario: Published message marked persistent

- **WHEN** the producer publishes any message
- **THEN** the message is sent with `DeliveryMode.PERSISTENT` so it is written to a durable queue and retained across a broker restart

### Requirement: Per-module domain event producers

The system SHALL provide per-module producers (for example `UserEventProducer` and `ClientEventProducer`) that subclass `EventProducer` and expose typed methods for each domain event, publishing the entity payload to the corresponding configured queue.

#### Scenario: User lifecycle events published to their queues

- **WHEN** `UserEventProducer.publish_user_created`, `publish_user_updated`, or `publish_user_deleted` is invoked
- **THEN** the serialized payload is published to `USER_CREATED_QUEUE`, `USER_UPDATED_QUEUE`, or `USER_DELETED_QUEUE` respectively

#### Scenario: Client events published to their queues

- **WHEN** `ClientEventProducer.publish_client_created` or `publish_client_updated` is invoked with a client response DTO
- **THEN** the serialized client payload is published to `CLIENT_CREATED_QUEUE` or `CLIENT_UPDATED_QUEUE` respectively

### Requirement: Producer integration in application services

Application services SHALL publish the corresponding domain event only after the primary state change has succeeded, so that a create, update, or delete emits its event once persisted.

#### Scenario: Event emitted after successful create

- **WHEN** a service `create` operation persists a new entity successfully
- **THEN** the service publishes the created event carrying the response DTO after persistence completes

#### Scenario: Delete emits a deletion event

- **WHEN** a service `delete` operation removes an entity successfully
- **THEN** the service publishes a deletion event carrying the entity identifier
