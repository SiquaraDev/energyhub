## Context

The platform is fully decomposed and orchestrated. Fase 15 turned the monolith into five services (`auth`, `client`, `contract`, `financial`, `audit`), each of which registers itself with Consul at startup through a shared helper (`discovery.py`, implemented over the Consul HTTP API with `httpx`) and deregisters on shutdown; the `audit-service` additionally runs an `AuditConsumer` background task that reads the `audit` queue and persists an `AuditLog` per message. Fase 16 placed every service behind a Kubernetes Deployment with multiple replicas and a Horizontal Pod Autoscaler.

Two defects inherited from Fase 15, both harmless in a single-instance run but active under Fase 16's scaling, are the subject of this change:

1. **Non-unique Consul `service_id`.** `register_with_consul` computes `service_id = f"{name}-{port}"`. Every replica of a Deployment runs the same image with the same `app_name` and `app_port`, so all replicas send the identical `ID` to their Consul agent. Consul treats a register with an existing `ID` as an *update*, so replicas overwrite one another; and `deregister_from_consul(service_id=...)` on any one pod's shutdown removes the shared entry for all of them. The catalog therefore reflects at most one instance and can flip to empty when a single pod stops — defeating discovery and load-balancing precisely when the HPA adds replicas.

2. **Audit queue with no producer.** `RabbitMQConfig.AUDIT_QUEUE = "audit"` is declared durable and the `AuditConsumer` consumes it, but no code path anywhere publishes an `AuditEvent` to it. The `AuditEvent` contract and the whole consumer/persistence path exist and are specified (`async-event-consumers`), yet the trail stays empty. The missing half is a producer plus the service-side calls that fire it.

The constraints are fixed by the earlier phases: the fix must stay within the existing per-service `discovery.py`, the existing `EventProducer`/`publish_safely` producer stack, the shared `AuditEvent` schema, and the `audit` queue name — without changing database schemas, Kubernetes manifests, or API contracts.

## Goals / Non-Goals

**Goals:**
- Give every running instance a Consul `service_id` that is unique per replica, so N replicas produce N distinct catalog entries that do not overwrite each other.
- Preserve name-based discovery and Traefik Consul-catalog routing by keeping the logical `Name` equal to `app_name` and only varying the `ID`.
- Deregister exactly the instance's own id on shutdown, so a stopping replica never removes a sibling's registration.
- Add an `AuditEventProducer` that publishes `AuditEvent` messages to the `audit` queue with the same robustness and persistence guarantees as the domain-event producers.
- Emit an audit event from each successful business write (create/update/delete) as a non-blocking side-effect, so the write remains the source of truth and a broker outage cannot roll it back.
- Prove the trail end to end: published audit events are consumed and persisted by the existing `AuditConsumer`.

**Non-Goals:**
- No change to the Consul health-check mechanics, the `Name`-based lookup used by callers/Traefik, or the deregister-on-critical policy.
- No change to the `AuditEvent` schema or the `AuditLog` persistence — both are specified in `async-event-consumers` and are unchanged here.
- **Amended during implementation:** this originally also excluded the `AuditConsumer`, on the premise that "the consumer side already works". That premise proved false. `AuditConsumer.start_consuming` calls `await queue.consume(...)`, which only *registers* the callback and returns; the coroutine then finished, its background task completed, and the local `connection` — the only live reference — was garbage-collected, silently tearing the subscription down. Observed live: the `audit` queue held messages with **0 consumers** and the `audit-service` had no AMQP connection at all, while running `start_consuming` by hand inside the container connected and received the pending message. The lifespan's own `consumer_task.cancel()` on shutdown only makes sense for a long-lived task, confirming the intent. Since this change's goal is to prove the trail end to end, shipping a producer feeding a queue nobody drains would merely mirror the very defect being fixed. The minimal fix — suspend `start_consuming` until cancellation so the connection stays referenced, closing it in a `finally` — is therefore **in scope**. The consumer's contract, prefetch, ack/requeue semantics and persistence are untouched.
- No Kubernetes manifest, Secret, ConfigMap, or database-schema edits; the pod `HOSTNAME` is already injected and requires no new plumbing.
- No move to exactly-once/transactional-outbox delivery for audit events — at-least-once with a best-effort side-effect is retained, consistent with the existing dual-write posture of `publish_safely`.
- No new audit *actions* or entity taxonomy beyond mapping the existing create/update/delete operations of the current services.

## Decisions

**Unique `service_id` from a pod-stable discriminator, logical `Name` unchanged:**
- **Decision:** Compute `service_id = f"{name}-{instance_id}"` where `instance_id` is the pod `HOSTNAME` environment variable when present, else a per-process `uuid4()`. Keep the Consul `Name` field equal to `app_name` and register the unique id in the `ID` field. The health check continues to target the same instance address/port.
- **Rationale:** In Kubernetes each pod's `HOSTNAME` is the pod name — unique, stable for the pod's lifetime, and already injected, so it is the natural per-replica discriminator and it makes a restarted pod's id human-traceable. The UUID fallback keeps the helper correct outside Kubernetes (Compose, local runs) where `HOSTNAME` may collide or be unset. Registering the unique value in `ID` while leaving `Name` as the logical service preserves name-based discovery and the Traefik Consul-catalog rules verbatim.
- **Alternatives considered:** Append the port only (status quo) — rejected, it is identical across replicas; use the pod IP — rejected, it is not exposed as conveniently as `HOSTNAME` and is less readable; use a random UUID always — rejected, it loses the pod-name traceability that aids debugging and cross-referencing with `kubectl`.

**Deregister the exact per-instance id captured at registration:**
- **Decision:** Continue to capture the returned `service_id` into the lifespan's `_service_id` and pass that same value to `deregister_from_consul` on shutdown; because the value is now unique, deregistration is inherently per-instance-safe.
- **Rationale:** The registration/deregistration symmetry already exists in each `main.py`; making the id unique is sufficient to fix the "one pod's shutdown deregisters the shared entry" failure without new lifecycle code. Consul's `DeregisterCriticalServiceAfter` still reaps instances whose pod is force-killed before shutdown runs.
- **Alternatives considered:** A cluster-wide reconciliation/cleanup job — rejected as unnecessary given the critical-service reaper already prunes stale ids; deregistering by `Name` — rejected, it would remove siblings, which is the very bug being fixed.

**Reuse `EventProducer` for a dedicated `AuditEventProducer`:**
- **Decision:** Add `AuditEventProducer(EventProducer)` exposing a typed `publish_audit(event: AuditEvent)` that publishes `event.model_dump(mode="json")` to `RabbitMQConfig.AUDIT_QUEUE`, mirroring `UserEventProducer`/`ClientEventProducer`. Expose a shared module-level instance and close it in the service's shutdown, like the existing producers.
- **Rationale:** The base class already provides lazy robust connection, durable-queue declaration, persistent delivery, and `MessagePublishingException` wrapping — exactly what the audit path needs. A dedicated typed producer keeps the `AuditEvent` contract explicit and matches the established per-module producer pattern.
- **Alternatives considered:** Publish raw dicts inline from services — rejected, it bypasses the typed contract and duplicates connection handling; route audit through Kafka instead of RabbitMQ — rejected, the consumer already listens on the RabbitMQ `audit` queue and switching brokers is out of scope.

**Emit audit events as a non-blocking side-effect after the primary write:**
- **Decision:** In each business service's create/update/delete, after the state change is persisted and the existing domain event is published, build an `AuditEvent` (actor from the current-user context, `action` = CREATE/UPDATE/DELETE, `entity_type`, `entity_id`, and a small `details` payload) and publish it through `publish_safely` so a `MessagePublishingException` is logged, not raised.
- **Rationale:** This matches the platform's existing dual-write stance (`publish_safely`): the persisted write is the source of truth and audit delivery is downstream and best-effort, so broker unavailability degrades to a rare missed audit event rather than a failed business operation. Firing after persistence guarantees the trail only records operations that actually happened.
- **Alternatives considered:** A transactional outbox for guaranteed audit delivery — deferred as a larger architectural change beyond these two gaps; emitting before persistence — rejected, it could record operations that later fail; making audit publication blocking/mandatory — rejected, it would let an audit-infra outage take down business writes.

**Resolve the actor from the existing current-user context:**
- **Decision:** Populate `AuditEvent.user_id` from the request's authenticated principal (the current-user resolution already used across the services). Where a write has no authenticated user in scope, use a defined system/actor sentinel rather than omitting the field.
- **Rationale:** The `AuditEvent` contract requires a `user_id`; reusing the current-user resolution keeps the "who" accurate without new plumbing, and a sentinel keeps the contract valid for system-initiated writes.
- **Alternatives considered:** Make `user_id` optional — rejected, it weakens the shared contract the consumer relies on; thread a new actor parameter through every layer — rejected as more invasive than reusing the established current-user dependency.

## Risks / Trade-offs

- **`HOSTNAME` absent or non-unique outside Kubernetes** → Fall back to a per-process `uuid4()` so the id is always unique; in Compose/local runs the id is still collision-free even if less readable.
- **Stale unique ids accumulate if a pod is force-killed before shutdown** → Consul's `DeregisterCriticalServiceAfter` (already set) reaps entries whose health check has been critical past the window, so orphaned per-instance ids self-clean.
- **Audit publication adds latency/failure surface to every write** → Publication is a post-persistence, non-blocking side-effect via `publish_safely`; a broker outage is logged and the write still succeeds, so the added surface cannot fail a business operation.
- **At-least-once audit delivery can duplicate entries** → Accepted, consistent with the existing consumer posture (`prefetch_count=1`, requeue-on-failure); the audit trail tolerates rare duplicates far better than gaps, and de-duplication can be layered later if needed.
- **Missed audit events under broker outage** → Accepted trade-off of the best-effort model; if a guaranteed trail is later required, a transactional outbox is the follow-up (noted in Open Questions), not part of this change.
- **Actor context missing for some writes** → A defined system sentinel keeps the `AuditEvent` valid; the alternative (dropping the event) would silently lose trail coverage.

## Migration Plan

1. Update `discovery.py` in each service to derive `instance_id` from `HOSTNAME` (UUID fallback), set `ID = f"{name}-{instance_id}"`, and keep `Name = app_name`; return the unique id. No `main.py` lifespan change is needed beyond continuing to store and later deregister the returned id.
2. Deploy and scale a Deployment to ≥2 replicas (or let the HPA scale it); confirm the Consul catalog shows one entry per replica and that stopping one pod removes only its own id.
3. Add `AuditEventProducer` (and a shared instance) to each business service alongside the existing producers, and close it in the shutdown path.
4. Wire create/update/delete in `user_service`, `client_service`, `contract_service`, `invoice_service` (and peers) to build an `AuditEvent` and publish it via `publish_safely` after the primary write.
5. Exercise a create/update/delete against each service and confirm the `audit-service` persists a matching `AuditLog` (query the audit read endpoint / auditdb).
6. Rollback: the registration change is a drop-in swap of the id derivation (revert `discovery.py`); the audit producer is additive (removing the `publish_safely` call and the producer restores prior behavior with no schema impact).

## Open Questions

- Should audit delivery move to a transactional outbox (or Kafka log) for a guaranteed, gap-free trail, given the compliance sensitivity of energy-trading records — or is best-effort at-least-once acceptable for now?
- Which write operations warrant an audit event beyond CRUD — should domain state transitions (e.g. contract approval, invoice payment) get distinct audit actions rather than a generic UPDATE?
- Should the per-instance `service_id` also embed the pod IP or a start timestamp to further disambiguate a pod name reused across restarts, or is `HOSTNAME` sufficient given Consul's critical-service reaping?
- Should audit events carry a correlation/request id so the trail can be joined to request logs and traces, and if so where is that id sourced?
