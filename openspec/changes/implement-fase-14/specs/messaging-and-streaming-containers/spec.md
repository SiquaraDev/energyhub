## ADDED Requirements

### Requirement: Containerized RabbitMQ broker

The system SHALL define a RabbitMQ service using a management-enabled image, exposing the AMQP port (`5672`) and the management UI port (`15672`), initialized with credentials supplied via environment variables.

#### Scenario: Broker and management UI are reachable

- **WHEN** the RabbitMQ container is running
- **THEN** the AMQP port accepts broker connections and the management UI is reachable on port `15672` using the configured credentials

#### Scenario: Broker reports healthy

- **WHEN** the RabbitMQ health check runs
- **THEN** `rabbitmq-diagnostics ping` succeeds and the service is marked healthy

### Requirement: Containerized Kafka with Zookeeper

The system SHALL define a Kafka service and its required Zookeeper service, with Kafka depending on Zookeeper and exposing the broker port (`9092`) for streaming.

#### Scenario: Kafka starts after Zookeeper

- **WHEN** the streaming services are started
- **THEN** Zookeeper starts first and Kafka connects to it via the configured `KAFKA_ZOOKEEPER_CONNECT` before becoming available

#### Scenario: Kafka broker accepts topic operations

- **WHEN** a client lists topics against `localhost:9092` inside the Kafka container
- **THEN** the broker responds successfully, confirming it is operational
