# messaging-and-streaming-containers Specification

## Purpose
TBD - created by archiving change implement-fase-14. Update Purpose after archive.
## Requirements
### Requirement: Containerized RabbitMQ broker

The system SHALL define a RabbitMQ service using a management-enabled image, exposing the AMQP port (`5672`) and the management UI port (`15672`), initialized with credentials supplied via environment variables.

#### Scenario: Broker and management UI are reachable

- **WHEN** the RabbitMQ container is running
- **THEN** the AMQP port accepts broker connections and the management UI is reachable on port `15672` using the configured credentials

#### Scenario: Broker reports healthy

- **WHEN** the RabbitMQ health check runs
- **THEN** `rabbitmq-diagnostics ping` succeeds and the service is marked healthy

### Requirement: Kafka broker in KRaft mode

The system SHALL run the Kafka broker in KRaft mode with a self-managed metadata quorum and no separate Zookeeper service, and in the Kubernetes deployment SHALL run it as a `StatefulSet` fronted by a headless `Service` for a stable network identity and ordered lifecycle, backed by PersistentVolumeClaim log storage, while continuing to expose the broker port (`9092`) for streaming.

#### Scenario: Kafka starts without Zookeeper

- **WHEN** the streaming workload is started
- **THEN** the broker forms its own metadata quorum in KRaft mode (`KAFKA_PROCESS_ROLES=broker,controller`) and becomes available with no Zookeeper service present and no `KAFKA_ZOOKEEPER_CONNECT` configured

#### Scenario: Broker has a stable identity as a StatefulSet

- **WHEN** Kafka is deployed to Kubernetes
- **THEN** it runs as a `StatefulSet` fronted by a headless `Service`, giving the broker a stable ordinal hostname and an ordered lifecycle rather than an interchangeable Deployment pod

#### Scenario: Broker log survives a pod restart

- **WHEN** the Kafka pod is deleted and rescheduled
- **THEN** the replacement pod re-attaches its PersistentVolumeClaim at `/var/lib/kafka/data` and retains its committed log rather than starting empty

#### Scenario: Kafka broker accepts topic operations

- **WHEN** a client lists topics against `kafka-service:9092`
- **THEN** the broker responds successfully, confirming it is operational

