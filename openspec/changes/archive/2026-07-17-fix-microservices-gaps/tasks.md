## 1. Unique Consul Service ID Per Instance

- [x] 1.1 In each service's `discovery.py`, derive an `instance_id` from the `HOSTNAME` environment variable, falling back to a per-process `uuid4()` when it is unset
- [x] 1.2 Set the Consul registration `ID` to `f"{name}-{instance_id}"` while keeping `Name` equal to `app_name`, and return the unique id from `register_with_consul`
- [x] 1.3 Keep the HTTP health check pointed at the instance's own address/port and leave `DeregisterCriticalServiceAfter` in place so orphaned ids self-reap
- [x] 1.4 Confirm each `main.py` lifespan stores the returned unique id in `_service_id` for later deregistration (no other lifespan change needed)

## 2. Per-Instance-Safe Deregistration

- [x] 2.1 Verify `deregister_from_consul` is called on shutdown with the exact unique `_service_id` captured at registration
- [x] 2.2 Scale a Deployment to two or more replicas (or trigger the HPA) and confirm the Consul catalog shows one entry per replica under the shared `app_name`
- [x] 2.3 Stop a single replica and confirm only its own id is removed while sibling registrations remain resolvable by name

## 3. Audit Event Producer

- [x] 3.1 Add an `AuditEventProducer(EventProducer)` to each business service that publishes an `AuditEvent` to `RabbitMQConfig.AUDIT_QUEUE` via a typed `publish_audit` method
- [x] 3.2 Serialize the event with `model_dump(mode="json")` and rely on the base producer's robust connection, durable-queue declaration, and persistent delivery
- [x] 3.3 Expose a shared module-level producer instance and close it in the service's shutdown path, mirroring the existing domain-event producers

## 4. Wire Audit Events Into Business Writes

- [x] 4.1 Resolve the actor for the `AuditEvent.user_id` from the existing current-user context, using a defined system sentinel when no authenticated user is in scope
- [x] 4.2 In each write operation of `user_service`, `client_service`, `contract_service`, `invoice_service` (and peers), build an `AuditEvent` with the action, entity type, entity id, and a small `details` payload after the primary write persists
- [x] 4.3 Publish the audit event through `publish_safely` after persistence so a broker outage is logged and swallowed rather than rolling back the write
- [x] 4.4 Map create/update/delete operations to distinct audit actions so the recorded trail differentiates them

## 5. End-to-End Audit Trail

- [x] 5.1 Exercise a create, update, and delete against each business service with the broker and `audit-service` available
- [x] 5.2 Confirm the `AuditConsumer` receives each event and persists a matching `AuditLog`, and that the payload validates against the shared `AuditEvent` contract
- [x] 5.3 Confirm audit records accumulate over repeated business activity (the trail is populated, not starved)

## 6. Validation

- [x] 6.1 Validate multi-replica discovery: catalog entries are unique per instance and survive a single replica's shutdown
- [x] 6.2 Validate the end-to-end audit path from a business write to a persisted `AuditLog`
- [x] 6.3 Run `openspec validate fix-microservices-gaps --strict` and confirm the change is valid
