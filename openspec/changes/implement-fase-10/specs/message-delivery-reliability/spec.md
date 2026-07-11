## ADDED Requirements

### Requirement: Typed publish-failure handling

The system SHALL define a shared `MessagePublishingException`, and producers MUST raise it (chained from the original error) when a publish fails, so callers receive a typed, domain-level failure rather than a raw client error.

#### Scenario: Publish failure surfaces a typed exception

- **WHEN** a broker publish operation raises an error
- **THEN** the producer logs the failure and raises `MessagePublishingException` with the original exception preserved as its cause

### Requirement: Durable messaging survives restart

Messaging SHALL be durable end to end: queues are declared durable and messages are published persistently, so that a broker restart does not lose enqueued-but-unconsumed messages.

#### Scenario: Unconsumed messages retained across restart

- **WHEN** messages are published to a durable queue and the broker restarts before they are consumed
- **THEN** the messages remain in the queue and are delivered once consumers reconnect

### Requirement: At-least-once acknowledgement

Consumers SHALL acknowledge a message only after its handler has processed it successfully, providing at-least-once delivery; an unacknowledged message MUST be redelivered.

#### Scenario: Message acknowledged after successful processing

- **WHEN** a consumer handler finishes processing a message without error
- **THEN** the message is acknowledged and removed from the queue

#### Scenario: Failed or interrupted processing triggers redelivery

- **WHEN** a handler fails or the consumer disconnects before acknowledging a message
- **THEN** the broker re-queues the message for redelivery so it is not silently lost

### Requirement: Messaging isolated from the primary transaction

Event publication SHALL occur after the primary state change has committed and MUST NOT roll back that operation if the broker is unavailable, keeping messaging as a non-blocking side effect of the write path.

#### Scenario: Primary write survives a broker outage

- **WHEN** a state change is persisted successfully but the subsequent event publish cannot reach the broker
- **THEN** the persisted state change is retained (not rolled back) and the publish failure is surfaced separately for handling
