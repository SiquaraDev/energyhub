## ADDED Requirements

### Requirement: Kafka and Zookeeper provisioning

The system SHALL provision Apache Kafka and its Zookeeper coordinator as Docker Compose services, with Kafka exposing port 9092 and depending on Zookeeper.

#### Scenario: Kafka broker starts with its coordinator

- **WHEN** the services are started via `docker-compose up -d zookeeper kafka`
- **THEN** Zookeeper is available on port 2181 and the Kafka broker starts, advertises its listener on port 9092, and becomes reachable

### Requirement: Kafka connection settings

The system SHALL expose the Kafka connection through `settings.kafka_bootstrap_servers` and the consumer group through `settings.kafka_group_id`, and streaming clients MUST read these values from configuration.

#### Scenario: Clients configured from settings

- **WHEN** a Kafka producer or consumer is created
- **THEN** it uses `settings.kafka_bootstrap_servers` for the bootstrap servers and, for consumers, `settings.kafka_group_id` for the consumer group

### Requirement: Topic definition

`KafkaConfig` SHALL declare the high-volume event topics (`user-events`, `client-events`, `contract-events`, `financial-events`) with an explicit partition count and replication factor per topic.

#### Scenario: Topic partitioning declared

- **WHEN** the topic configuration is read
- **THEN** each declared topic specifies its number of partitions and replication factor (for example the financial topic uses more partitions to absorb higher throughput)

### Requirement: Idempotent topic creation

`KafkaConfig` SHALL provide an async `create_topics()` operation that creates the declared topics and MUST tolerate topics that already exist without failing.

#### Scenario: Topics created on first run

- **WHEN** `create_topics()` runs against a broker with none of the topics present
- **THEN** every declared topic is created with its configured partitions and replication factor

#### Scenario: Existing topics do not cause failure

- **WHEN** `create_topics()` runs against a broker where the topics already exist
- **THEN** the operation completes without raising, leaving the existing topics unchanged
