## RENAMED Requirements

- FROM: `### Requirement: Containerized Kafka with Zookeeper`
- TO: `### Requirement: Kafka broker in KRaft mode`

## MODIFIED Requirements

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
