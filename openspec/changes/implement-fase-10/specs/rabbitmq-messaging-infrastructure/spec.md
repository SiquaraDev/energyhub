## ADDED Requirements

### Requirement: RabbitMQ broker provisioning

The system SHALL provision a RabbitMQ broker as a Docker Compose service exposing the AMQP port (5672) and the management UI port (15672), configured with the application credentials, a healthcheck, and a persistent named volume for its data.

#### Scenario: Broker starts and reports healthy

- **WHEN** the RabbitMQ service is started via `docker-compose up -d rabbitmq`
- **THEN** the container passes its `rabbitmq-diagnostics ping` healthcheck and the management UI is reachable on port 15672 with the configured credentials

#### Scenario: Broker state survives a restart

- **WHEN** the RabbitMQ container is restarted
- **THEN** durable queues and their persisted messages are still present because the data directory is backed by a persistent volume

### Requirement: Broker connection settings

The system SHALL expose the broker connection through `settings.rabbitmq_url`, and `RabbitMQConfig` SHALL resolve the connection URL from that single configuration source rather than hardcoding it at call sites.

#### Scenario: URL resolved from settings

- **WHEN** `RabbitMQConfig.get_url()` is called
- **THEN** it returns the value of `settings.rabbitmq_url` so all producers and consumers connect through one configured endpoint

### Requirement: Queue topology definition

`RabbitMQConfig` SHALL centralize the queue-name constants for every domain event stream (user created/updated/deleted, client created/updated, contract created/approved, invoice issued/paid, notification, and audit) so producers and consumers reference the same identifiers.

#### Scenario: Named queue constants are shared

- **WHEN** a producer and a consumer each reference a queue by its `RabbitMQConfig` constant
- **THEN** both resolve to the identical queue name, preventing routing mismatches from typos

### Requirement: Idempotent durable queue declaration

The system SHALL provide a `setup_queues()` helper that declares every configured queue as durable, and declaration MUST be idempotent so re-running it against an existing broker leaves the topology unchanged.

#### Scenario: Queues declared at startup

- **WHEN** `setup_queues()` runs against a broker
- **THEN** each configured queue exists and is declared `durable=True`

#### Scenario: Re-declaration is safe

- **WHEN** `setup_queues()` runs a second time against a broker that already has the queues
- **THEN** it completes without error and does not create duplicate or altered queues
