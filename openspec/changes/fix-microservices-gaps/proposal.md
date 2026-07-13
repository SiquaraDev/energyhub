## Why

Fase 15 decomposed the monolith into independent services — each registers itself in Consul (via the `httpx` HTTP API) under a `service_id` of `"{name}-{port}"`, and the `audit-service` consumes an `audit` queue — and Fase 16 placed every service behind a multi-replica Deployment with a Horizontal Pod Autoscaler. Two latent defects from that decomposition now surface under scale: because the Consul `service_id` is derived only from name and port, sibling replicas register the *same* id and overwrite/deregister each other in the catalog, breaking discovery and load-balancing exactly when the HPA scales out; and because no service ever publishes to the `audit` queue, the `AuditConsumer` starves and the audit trail — a compliance-critical record for an energy-trading backend — is never populated. This change closes both gaps so the platform behaves correctly under the horizontal scaling the earlier phases introduced.

## What Changes

- Make each service's Consul `service_id` unique per running instance by appending a per-instance discriminator — the Kubernetes pod `HOSTNAME`, falling back to a per-process UUID — to the logical service name, so N replicas register N distinct ids instead of colliding on `{name}-{port}`.
- Keep the logical registration `Name` equal to `app_name` (so name-based discovery and Traefik Consul-catalog routing are unaffected) while registering and health-checking each instance under its own unique id.
- Deregister exactly the instance's own unique id on shutdown, so a stopping or rescheduled replica removes only its own catalog entry and never a sibling's.
- Add an `AuditEventProducer` (subclass of the existing `EventProducer`) that publishes a well-formed `AuditEvent` to the `audit` queue using the same robust-connection, persistent-delivery mechanics as the domain-event producers.
- Wire the write operations of the business services (auth, client, contract, financial) to emit an audit event after each successful create/update/delete, published as a non-blocking side-effect via `publish_safely`, so a broker outage never rolls back the already-persisted write.
- Populate the audit trail end to end: events published to the `audit` queue are consumed by the existing `AuditConsumer` and persisted as `AuditLog` rows, so the trail reflects real business activity for the first time.

## Capabilities

### New Capabilities

- `audit-event-production`: An `AuditEventProducer` plus service-side wiring that publishes `AuditEvent` messages to the `audit` queue for business write operations, closing the producer gap so the existing audit consumer receives and records them end to end.

### Modified Capabilities

- `service-discovery`: The Consul-registration requirement changes so each instance's `service_id` is unique per replica (pod `HOSTNAME`/UUID discriminator instead of `name-port`), and a new requirement covers per-instance-safe deregistration on shutdown.
- `domain-event-producers`: The application-service producer-integration requirement changes so that, in addition to the existing domain event, each successful write also emits an audit event as a non-blocking side-effect.

## Impact

- **Dependencies**: No new runtime dependencies — reuses `httpx` (Consul HTTP API), `aio-pika` (RabbitMQ), and the existing `EventProducer`/`publish_safely` machinery. Relies on the Kubernetes-injected pod `HOSTNAME` environment variable (present by default in every pod) for the instance discriminator, with a per-process UUID fallback when it is absent.
- **Consumes**: Fase 15's `discovery.py` (Consul register/deregister helpers), the `EventProducer`/`publish_helper` producer stack, the shared `AuditEvent` contract, `RabbitMQConfig.AUDIT_QUEUE`, and the `audit-service` `AuditConsumer`; Fase 16's multi-replica Deployments/HPA that expose the `service_id` collision.
- **Provides**: Correct per-instance Consul registration under horizontal scaling (no self-deregistration between siblings), and a populated, end-to-end audit trail.
- **Affected code**: `services/*/src/energyhub/discovery.py` and each service's `main.py` lifespan (unique registration id + matching deregistration); a new `audit_event_producer.py` in each business service and the application services that perform writes (`user_service.py`, `client_service.py`, `contract_service.py`, `invoice_service.py`, and peers). No database schema, secret, or Kubernetes manifest changes are required — the pod `HOSTNAME` is already injected.
- **Coordination**: Additive to running behavior — no new secrets, no manifest edits, no API-contract changes. The `audit` queue name and the `AuditEvent` schema remain the shared source of truth between producer and the existing consumer.
