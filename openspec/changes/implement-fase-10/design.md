## Context

Through Fase 9 the platform is fully synchronous: application services do their own side work (notifications, audit logging, downstream updates) inline within the request. That couples otherwise independent modules and pushes non-essential work onto the response latency. This phase introduces an asynchronous messaging layer inside the existing Clean Architecture layout so modules exchange events instead of calling each other directly.

Two brokers are used deliberately for two shapes of traffic. RabbitMQ handles reliable, per-entity workflow events (a user was created, a contract was approved) where routing to a specific consumer and at-least-once delivery matter. Kafka handles high-volume event streams (`user-events`, `client-events`, `contract-events`, `financial-events`) where partitioned throughput and replayable, group-based consumption matter. Both are provisioned via the existing `docker-compose.yml` alongside PostgreSQL and Redis.

The stack is fixed by the plan: `aio-pika` for RabbitMQ and `aiokafka` for Kafka, both async to match the FastAPI/asyncio runtime. Configuration is single-sourced through `energyhub.config.settings` (`rabbitmq_url`, `kafka_bootstrap_servers`, `kafka_group_id`). Messaging code lives under `shared/infrastructure/messaging/` with per-module producers/consumers under each module's `infrastructure/messaging/`, keeping infrastructure concerns out of the domain and application layers.

## Goals / Non-Goals

**Goals:**
- Provision RabbitMQ, Kafka, and Zookeeper as Docker services with credentials, healthchecks, and persistent storage.
- Define RabbitMQ queue topology (`RabbitMQConfig`) and idempotent durable-queue setup; define Kafka topic topology (`KafkaConfig`) and idempotent topic creation.
- Provide a generic `EventProducer` base and per-module domain producers, wired into services so events publish after a successful state change.
- Provide async consumers (`NotificationConsumer`, `AuditConsumer`) with manual acknowledgement and bounded prefetch, plus the `AuditEvent` contract.
- Provide `KafkaEventProducer`/`KafkaEventConsumer` for high-volume keyed streams.
- Guarantee delivery reliability: durability, at-least-once acks, and typed publish-failure handling isolated from the primary transaction.

**Non-Goals:**
- No new domain entities or business rules — messaging only transports events derived from existing DTOs/entities.
- No exchange topology beyond the default exchange for RabbitMQ (direct routing-key to queue); no dead-letter/retry exchange in this phase.
- No schema registry, Avro/Protobuf, or exactly-once semantics for Kafka — JSON payloads and at-least-once are sufficient here.
- No production hardening (clustering, TLS, mirrored queues, multi-broker replication) — single-node dev topology with replication factor 1.
- No orchestration of consumer processes/workers as deployables (Fase 11+ / ops concern).

## Decisions

**Two brokers, split by traffic shape (RabbitMQ for workflows, Kafka for streams):**
- **Decision:** Route per-entity workflow events through RabbitMQ queues and high-volume analytical/event streams through Kafka topics, as the plan prescribes.
- **Rationale:** RabbitMQ's per-message routing, durability, and manual ack fit targeted at-least-once workflows (notify one consumer, write one audit row); Kafka's partitions, consumer groups, and retained log fit high-throughput, replayable streams. Using each for its strength avoids forcing one broker into the other's role.
- **Alternative considered:** A single broker for everything — rejected; RabbitMQ scales poorly for high-volume replayable streams and Kafka is awkward for targeted per-message workflows, and the plan explicitly specifies both.

**Generic `EventProducer` base with per-module subclasses:**
- **Decision:** A shared `EventProducer` owns the robust connection/channel and the `publish(queue, message)` primitive; `UserEventProducer`, `ClientEventProducer`, etc. subclass it and expose typed per-event methods.
- **Rationale:** Centralizes connection management, serialization, and error handling in one place while giving each module a small, typed surface; removes duplicated connect/publish boilerplate.
- **Alternative considered:** One monolithic producer with a method per event across all modules — rejected; it couples every module to one class and bloats it, breaking module boundaries.

**Publish after commit, as a non-blocking side effect:**
- **Decision:** Services publish the event only after the primary persistence has succeeded; a broker failure surfaces as `MessagePublishingException` but does not roll back the committed state change.
- **Rationale:** The write is the source of truth; messaging is downstream. Rolling back a persisted operation because a notification failed would be worse than a missed event, and consumers tolerate at-least-once anyway.
- **Alternative considered:** Transactional outbox (persist event + state in one transaction, relay later) — stronger consistency but adds an outbox table, a relay worker, and polling; deferred as over-engineering for this phase and noted as an open question for later.

**Manual acknowledgement with `prefetch_count=1` on consumers:**
- **Decision:** Consumers process inside `message.process()` (ack on success) and set QoS prefetch to 1.
- **Rationale:** Ack-after-processing yields at-least-once delivery so a crash mid-handler re-queues the message; prefetch 1 spreads load evenly and prevents one worker from hoarding the queue.
- **Alternative considered:** Auto-ack with higher prefetch — rejected; auto-ack loses messages on handler failure, and high prefetch unbalances work across consumers.

**Durable queues + persistent delivery; Kafka replication factor 1 in dev:**
- **Decision:** Declare all RabbitMQ queues `durable=True` and publish with `DeliveryMode.PERSISTENT`; declare Kafka topics with per-topic partitions and replication factor 1.
- **Rationale:** Durability/persistence let unconsumed messages survive a broker restart, matching the reliability requirements. Replication factor 1 is correct for a single-node dev broker; higher factors need a multi-broker cluster that is out of scope.
- **Alternative considered:** Transient queues/messages — rejected; they drop unconsumed messages on restart, defeating the reliability goal.

**Idempotent topology setup for both brokers:**
- **Decision:** `setup_queues()` re-declares durable queues (a no-op if present) and `KafkaConfig.create_topics()` swallows "topic already exists" so both can run on every startup.
- **Rationale:** Startup routines must be safe to re-run; declaration is naturally idempotent in AMQP and can be made so for Kafka by tolerating the exists error.
- **Alternative considered:** One-time manual provisioning scripts — rejected; they drift from code and fail on fresh environments.

## Risks / Trade-offs

- **Dual-write inconsistency (state committed, event never published)** → Publish-after-commit means a broker outage can drop an event while the write persists. Mitigation: surface `MessagePublishingException` for logging/alerting, keep consumers idempotent-tolerant, and record a transactional outbox as a future option if guaranteed delivery becomes required.
- **At-least-once implies duplicate deliveries** → A re-queued or replayed message can be processed twice. Mitigation: design consumer handlers (notifications, audit) to be idempotent or naturally repeat-safe; use stable keys where dedup matters.
- **Broker availability becomes a new operational dependency** → Producers/consumers fail if RabbitMQ/Kafka are down. Mitigation: `aio-pika` robust connections auto-reconnect; publishing is non-blocking to the write path; healthchecks and `depends_on` order container startup.
- **Consumers are unmanaged in this phase** → The specs define consumer behavior but not how consumer processes are deployed/supervised. Mitigation: treat wiring consumers into a runnable entrypoint as a follow-up ops task; this phase validates them against the running brokers.
- **Two brokers add cognitive and infra overhead** → More moving parts to learn and run locally. Mitigation: clear split of responsibilities (workflows vs. streams), shared config/exception, and Docker Compose so the whole stack comes up with one command.
- **JSON payloads are schema-less** → No schema enforcement across producer/consumer versions. Mitigation: typed producer methods and the `AuditEvent` model act as the contract; a schema registry is deferred.

## Migration Plan

1. Add RabbitMQ (with management UI, healthcheck, persistent volume) to `docker-compose.yml`, add `aio-pika`, and expose `settings.rabbitmq_url`; bring the broker up and confirm the management UI.
2. Add `RabbitMQConfig` (queue constants + `get_url`) and `setup_queues()`; run setup and confirm the durable queues exist.
3. Add `EventProducer`, the shared `MessagePublishingException`, and the per-module producers; wire producers into the services so events publish after create/update/delete.
4. Add `NotificationConsumer`, `AuditConsumer`, and the `AuditEvent` model; verify events flow producer → queue → consumer and that audit events persist.
5. Add Kafka + Zookeeper to `docker-compose.yml`, add `aiokafka`, expose `settings.kafka_bootstrap_servers`/`kafka_group_id`; bring the brokers up.
6. Add `KafkaConfig` with topics and `create_topics()`; add `KafkaEventProducer`/`KafkaEventConsumer`; verify keyed publish/consume round-trips per topic.
7. Rollback: this phase is additive (new infra services + new code). Reverting the branch and removing the added Docker services removes the messaging layer without touching existing data.

## Open Questions

- Should a transactional outbox be introduced to guarantee event delivery, or is publish-after-commit with alerting acceptable until a consumer requires stronger guarantees? (Current plan: publish-after-commit; revisit if a downstream needs exactly-once-effect.)
- Should RabbitMQ use a topic/direct exchange with routing keys instead of publishing to the default exchange per queue, to support fan-out and dead-lettering? (Deferred; default exchange is sufficient for the current one-queue-per-event model.)
- Where do consumer processes run — a dedicated worker entrypoint, background tasks in the API process, or separate deployables? (Deferred to an ops/deployment task after the behavior is validated.)
- Which events belong on Kafka versus RabbitMQ as the model grows (some events may warrant both)? (Current plan follows the fixed lists in the phase doc; revisit per event as volume data arrives.)
