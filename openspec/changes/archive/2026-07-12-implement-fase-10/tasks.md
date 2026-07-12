## 1. RabbitMQ Broker Provisioning

- [x] 1.1 Add a `rabbitmq` service (image `rabbitmq:3-management-alpine`) to `docker-compose.yml` exposing ports 5672 and 15672 with the application credentials
- [x] 1.2 Add a `rabbitmq-diagnostics ping` healthcheck and a persistent `rabbitmq_data` volume to the service
- [x] 1.3 Add `aio-pika` to `pyproject.toml` and install it (`poetry add aio-pika`)
- [x] 1.4 Add `rabbitmq_url` to `Settings` in `energyhub/config.py`
- [x] 1.5 Bring the broker up (`docker-compose up -d rabbitmq`) and confirm the management UI is reachable on port 15672 with the configured credentials

## 2. Queue Topology

- [x] 2.1 Create `RabbitMQConfig` in `shared/infrastructure/messaging/` with the queue-name constants for user, client, contract, invoice, notification, and audit events
- [x] 2.2 Add `RabbitMQConfig.get_url()` returning `settings.rabbitmq_url`
- [x] 2.3 Create the `setup_queues()` helper that connects and declares every configured queue as `durable=True`
- [x] 2.4 Run `setup_queues()` and confirm the durable queues appear in the management UI; re-run it and confirm it is idempotent (no errors, no duplicates)

## 3. Event Producers

- [x] 3.1 Create the shared `MessagePublishingException` in `shared/domain/exception/`
- [x] 3.2 Create the `EventProducer` base in `shared/infrastructure/messaging/` with `connect`/`disconnect` and an async `publish(queue, message)` that JSON-encodes the payload
- [x] 3.3 Publish with `DeliveryMode.PERSISTENT` and wrap failures in `MessagePublishingException` (chained from the original error) with logging
- [x] 3.4 Create `UserEventProducer` in `auth/infrastructure/messaging/` with `publish_user_created`/`publish_user_updated`/`publish_user_deleted`
- [x] 3.5 Create `ClientEventProducer` in `clients/infrastructure/messaging/` with `publish_client_created`/`publish_client_updated`
- [x] 3.6 Inject the producers into the corresponding services and publish the event after each successful create/update/delete
- [x] 3.7 Trigger a create through a service and confirm the message lands on its queue

## 4. Async Consumers

- [x] 4.1 Create the `AuditEvent` model in `shared/infrastructure/messaging/` with `user_id`, `action`, `entity_type`, `entity_id`, and `details`
- [x] 4.2 Create `NotificationConsumer` in `notifications/infrastructure/messaging/` with handlers for user-created, client-created, contract-approved, and invoice-issued events
- [x] 4.3 Implement `NotificationConsumer.start_consuming()` declaring the durable queues, setting `prefetch_count=1`, and registering the handlers
- [x] 4.4 Create `AuditConsumer` in `audit/infrastructure/messaging/` that constructs an `AuditLog` from the event and saves it via `AuditLogRepository`
- [x] 4.5 Implement `AuditConsumer.start_consuming()` for the audit queue with `prefetch_count=1` and process-based acknowledgement
- [x] 4.6 Publish a test event end to end and confirm the consumer processes it and (for audit) persists an `AuditLog`

## 5. Kafka Provisioning

- [x] 5.1 Add `zookeeper` (image `confluentinc/cp-zookeeper`) to `docker-compose.yml` exposing port 2181
- [x] 5.2 Add `kafka` (image `confluentinc/cp-kafka`) depending on `zookeeper`, exposing port 9092 and advertising its listener
- [x] 5.3 Add `aiokafka` to `pyproject.toml` and install it (`poetry add aiokafka`)
- [x] 5.4 Add `kafka_bootstrap_servers` and `kafka_group_id` to `Settings` in `energyhub/config.py`
- [x] 5.5 Bring the brokers up (`docker-compose up -d zookeeper kafka`) and confirm Kafka is reachable on port 9092

## 6. Kafka Topics

- [x] 6.1 Create `KafkaConfig` in `shared/infrastructure/messaging/` declaring `user-events`, `client-events`, `contract-events`, and `financial-events` with per-topic partitions and replication factor
- [x] 6.2 Implement async `KafkaConfig.create_topics()` using `AIOKafkaAdminClient`, tolerating topics that already exist
- [x] 6.3 Run `create_topics()` and confirm every topic exists with the configured partition count; re-run and confirm it does not fail

## 7. Kafka Event Streaming

- [x] 7.1 Create `KafkaEventProducer` in `shared/infrastructure/messaging/` with `start`/`stop` and an async `publish(topic, key, message)` that JSON-serializes the value and awaits acknowledgement
- [x] 7.2 Wrap Kafka publish failures in `MessagePublishingException` with logging
- [x] 7.3 Integrate the Kafka producer into services for high-volume events, sending each event under a partition key
- [x] 7.4 Create `KafkaEventConsumer` in `shared/infrastructure/messaging/` with per-topic consume methods (`consume_user_events`, `consume_client_events`, `consume_financial_events`) using `settings.kafka_group_id`
- [x] 7.5 Deserialize each JSON message and stop the consumer in a `finally` block
- [x] 7.6 Publish and consume a keyed event round-trip and confirm same-key events reach the same partition in order

## 8. Delivery Reliability

- [x] 8.1 Verify queues are declared durable and messages are published persistently by restarting the broker and confirming unconsumed messages survive
- [x] 8.2 Verify consumers acknowledge only after successful processing and that an interrupted handler causes redelivery
- [x] 8.3 Verify a broker outage during publish surfaces `MessagePublishingException` without rolling back the committed state change

## 9. Validation

- [x] 9.1 Confirm RabbitMQ, Kafka, and Zookeeper start via Docker Compose and pass their healthchecks
- [x] 9.2 Confirm producers publish and consumers process events for every configured queue and topic
- [x] 9.3 Run `openspec validate implement-fase-10` and confirm the change is valid
