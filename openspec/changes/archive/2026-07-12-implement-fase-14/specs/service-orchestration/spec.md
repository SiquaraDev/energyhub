## ADDED Requirements

### Requirement: Compose defines the full service stack

The system SHALL provide a `docker-compose.yml` that defines the `energyhub-api` service together with every runtime dependency: PostgreSQL, Redis, RabbitMQ, Elasticsearch, Kafka, Zookeeper, Prometheus, and Grafana.

#### Scenario: All services start with one command

- **WHEN** `docker-compose up -d` is run from the project root
- **THEN** every defined service is created and started, and `docker-compose ps` lists them as running

### Requirement: Shared bridge network

All services SHALL be attached to a single shared bridge network so they can reach each other by service name.

#### Scenario: Services resolve each other by name

- **WHEN** the API container connects to `postgres`, `redis`, `rabbitmq`, or `elasticsearch`
- **THEN** the hostnames resolve to the corresponding service containers over the shared network

### Requirement: Health-gated startup ordering

The API service SHALL declare `depends_on` conditions so that it starts only after the services that expose a health check report healthy.

#### Scenario: API waits for healthy dependencies

- **WHEN** the stack is started and a health-checked dependency (e.g. PostgreSQL or Elasticsearch) is not yet healthy
- **THEN** the API container does not start until that dependency's health check passes

### Requirement: Restart policy for resilience

Every long-running service SHALL declare `restart: unless-stopped` so containers recover automatically after failures or host restarts.

#### Scenario: Service recovers after an unexpected exit

- **WHEN** a running service container exits unexpectedly and was not explicitly stopped
- **THEN** Docker restarts the container automatically
