## Why

Through Fase 9 every operation runs synchronously inside the request path: creating a user, a client, or an invoice does its own side work (notifications, audit trail) inline, coupling unrelated modules and slowing responses. This phase introduces asynchronous messaging so modules communicate through events instead of direct calls — RabbitMQ for reliable per-entity workflows and Kafka for high-volume event streams — decoupling producers from consumers.

## What Changes

- Provision a RabbitMQ broker (with management UI, healthcheck, credentials, and a persistent volume) in `docker-compose.yml`, add the `aio-pika` dependency, and expose `settings.rabbitmq_url`.
- Add a `RabbitMQConfig` that centralizes queue-name constants (user/client/contract/invoice/notification/audit) and resolves the broker URL from settings, plus a `setup_queues()` helper that declares every durable queue idempotently at startup.
- Add a generic `EventProducer` base (robust connection, persistent delivery) and per-module producers (`UserEventProducer`, `ClientEventProducer`, …) exposing typed publish methods; wire them into the application services so events are published after a successful state change (create/update/delete).
- Add async consumers: a `NotificationConsumer` that reacts to user-created, client-created, contract-approved, and invoice-issued events, and an `AuditConsumer` that persists an audit log from each `AuditEvent`, both using manual acknowledgement and bounded prefetch.
- Provision Kafka and Zookeeper in `docker-compose.yml`, add the `aiokafka` dependency, and expose `settings.kafka_bootstrap_servers` / `settings.kafka_group_id`; add a `KafkaConfig` that declares topics (with partition/replication factors) and creates them idempotently.
- Add a `KafkaEventProducer` (keyed JSON publishing) and a `KafkaEventConsumer` (per-topic consumption within a consumer group) for high-volume user/client/contract/financial event streams.
- Add a shared `MessagePublishingException` and reliability guarantees: durable queues and persistent messages that survive a broker restart, at-least-once delivery via post-processing acknowledgement, and publish failures that surface as a typed exception without corrupting state.

## Capabilities

### New Capabilities

- `rabbitmq-messaging-infrastructure`: RabbitMQ broker provisioning, connection settings, `RabbitMQConfig` queue topology, and idempotent durable-queue declaration at startup.
- `domain-event-producers`: A generic `EventProducer` base and per-module producers that publish typed domain events from the application services after successful state changes.
- `async-event-consumers`: Consumers (`NotificationConsumer`, `AuditConsumer`) that subscribe to queues and process user, client, contract, invoice, and audit events off the request path.
- `kafka-streaming-infrastructure`: Kafka/Zookeeper provisioning, streaming settings, and a `KafkaConfig` that declares and idempotently creates high-volume event topics.
- `kafka-event-streaming`: A `KafkaEventProducer` and `KafkaEventConsumer` that publish and consume keyed JSON events per topic within a consumer group for high-volume streams.
- `message-delivery-reliability`: Cross-cutting guarantees — durable/persistent messaging, at-least-once acknowledgement, and typed publish-failure handling via `MessagePublishingException`.

### Modified Capabilities

None — this phase introduces the messaging layer; no previously specified requirements change.

## Impact

- **Dependencies**: Adds `aio-pika` (RabbitMQ client) and `aiokafka` (Kafka client) to `pyproject.toml`. Adds RabbitMQ, Kafka, and Zookeeper services to `docker-compose.yml`.
- **Consumes**: Domain entities, DTOs, and application services from Fase 3–8; `energyhub.config.settings`; the `AuditLog` entity and `AuditLogRepository` from the persistence layer (Fase 5) for the audit consumer; the running Docker/Redis environment from the prior phases.
- **Provides**: `RabbitMQConfig`/`setup_queues`, the producer/consumer classes, `KafkaConfig`, the Kafka producer/consumer, and the shared `MessagePublishingException` — the asynchronous backbone that later phases (search indexing, integrations) build on.
- **New artifacts**: `shared/infrastructure/messaging/` (RabbitMQ config, `EventProducer`, Kafka config/producer/consumer, `AuditEvent`), per-module `infrastructure/messaging/` (domain producers/consumers), and `shared/domain/exception/message_publishing_exception.py`.
- **Coordination**: Messaging is additive and fire-and-forget relative to the transactional write path — events are published after the state change succeeds; a broker outage must not roll back the primary operation, and consumers are idempotent-tolerant given at-least-once delivery.
