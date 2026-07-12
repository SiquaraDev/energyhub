# kafka-event-streaming Specification

## Purpose
TBD - created by archiving change implement-fase-10. Update Purpose after archive.
## Requirements
### Requirement: Kafka event producer

The system SHALL provide a `KafkaEventProducer` with an explicit `start`/`stop` lifecycle that publishes keyed JSON events to a topic for high-volume streams.

#### Scenario: Producer lifecycle managed explicitly

- **WHEN** `start()` is called and later `stop()` is called
- **THEN** the underlying async Kafka producer is created and connected on start and cleanly closed on stop

#### Scenario: Keyed message published and acknowledged

- **WHEN** `publish(topic, key, message)` is called
- **THEN** the message value is JSON-serialized, published to the topic under the given key, and the call awaits broker acknowledgement before returning

### Requirement: Kafka event consumer

The system SHALL provide a `KafkaEventConsumer` that consumes events from a topic within the configured consumer group, deserializing each JSON message for processing.

#### Scenario: Consumer reads events within its group

- **WHEN** a per-topic consume method (for example `consume_user_events`) is started
- **THEN** it subscribes to that topic under `settings.kafka_group_id`, iterates delivered messages, deserializes each JSON value, and processes it

#### Scenario: Consumer stops cleanly

- **WHEN** consumption ends or is cancelled
- **THEN** the consumer is stopped in a `finally` block so offsets and connections are released regardless of how the loop exits

### Requirement: Key-based partition routing

The producer SHALL send each event with a partition key so that events sharing a key are routed to the same partition and their relative order is preserved.

#### Scenario: Same key preserves ordering

- **WHEN** multiple events are published to a topic with the same key
- **THEN** they are routed to the same partition, preserving their published order for consumers of that partition

