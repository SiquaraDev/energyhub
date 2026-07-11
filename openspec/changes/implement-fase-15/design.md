## Context

Through Fase 14 the platform is a modular monolith: cohesive modules (Auth, Clients, Contracts, Negotiations, Financial, Audit, Notifications, Reports) live in one codebase, share one process, and share one database. That structure ships and scales as a unit — a change to any module redeploys all of them, and load on one module competes for the same process resources as every other. The modules already have clear boundaries and a mostly acyclic dependency graph, which makes them viable seams for a split.

This phase extracts several of those modules into independently deployable FastAPI services that communicate over the network. The stack for this phase is fixed by the plan: FastAPI per service, Consul for service discovery, `httpx` for synchronous inter-service calls, `tenacity` for resilience, and Traefik as the API gateway. The containerized environment from the earlier infrastructure phases is a prerequisite, as is the existing event bus (RabbitMQ/Kafka) that Audit and Notifications consume.

The split is deliberately partial: Auth, Clients, Contracts, Financial, and Audit are extracted first because they anchor the dependency graph and exercise every communication and resilience pattern the remaining contexts will reuse. This is a topology change and an architectural pattern change spanning every module, which is why it warrants a design document.

## Goals / Non-Goals

**Goals:**
- Identify the bounded contexts and their dependency graph, and record them in `docs/bounded-contexts.md`.
- Extract Auth, Clients, Contracts, Financial, and Audit into standalone FastAPI services, each with its own project, config, database, container image, and `/health` endpoint.
- Register every service in Consul with an HTTP health check and resolve dependencies by logical name.
- Replace former in-process cross-module calls with `httpx` clients that preserve the dependency direction.
- Apply timeout, retry-with-backoff, and fallback resilience to every inter-service call.
- Route external traffic through a Traefik gateway by path prefix, with global auth, logging, and rate limiting at the edge.

**Non-Goals:**
- No rewrite of domain logic — extraction carries over each module's existing entities, repositories, services, routers, DTOs, and mappers unchanged in behavior.
- No extraction of Negotiations, Notifications, or Reports in this phase (they follow the same blueprint later).
- No distributed transactions, sagas, or eventual-consistency reconciliation beyond the existing event flow (deferred to the orchestration phase).
- No shared read-only database access as a shortcut — data crossing a context boundary goes through that context's service.
- No autoscaling, service mesh, or mTLS between services (later infrastructure phases).

## Decisions

**Split along existing module boundaries, extracting the dependency roots first:**
- **Decision:** Use the current modules as bounded contexts and extract in dependency order — Auth (no upstream), then Clients, Contracts, Financial, and Audit — rather than starting with a leaf module.
- **Rationale:** The modules already encapsulate their domains, so they are natural seams. Extracting Auth first means every later service can immediately depend on a real Auth service instead of a stub, and the first extraction validates the discovery/communication/resilience stack end to end.
- **Alternative considered:** "Strangler" extraction of a low-risk leaf module first — rejected because the leaves depend on Auth, so they would need Auth stubs anyway, deferring the hard integration work rather than de-risking it.

**Synchronous HTTP (`httpx`) for inter-service calls, keeping events for what is already event-driven:**
- **Decision:** Replace in-process cross-module calls with per-dependency async `httpx` clients (`AuthClient`, `ClientClient`, `ContractClient`); leave Audit and Notifications on the existing event bus.
- **Rationale:** The former calls were synchronous request/response (fetch a user, fetch a client), which maps directly onto HTTP clients and keeps the change mechanical and reviewable. Audit/Notifications are already fire-and-forget consumers, so they stay on events.
- **Alternative considered:** Convert all inter-service interactions to asynchronous messaging — rejected as over-scoped for this phase; it would rewrite request/response call sites into choreography and complicate reads that need an immediate answer.

**Database-per-service, no shared tables:**
- **Decision:** Each extracted service owns its own database/schema; cross-context data is fetched from the owning service, never by reaching into another service's tables.
- **Rationale:** A shared database would recreate the coupling the split is meant to remove and block independent deployment/scaling. Per-service ownership makes each context the single writer of its data.
- **Alternative considered:** One shared database with per-service schemas and cross-schema reads — rejected; it is operationally simpler short-term but reintroduces hidden coupling and defeats independent evolution.

**Consul for discovery with HTTP health checks; callers resolve by logical name:**
- **Decision:** Each service self-registers in Consul on startup with a `/health` check, and callers look up dependencies by logical name rather than static host/port.
- **Rationale:** Instances move between hosts and ports in a containerized environment; name-based resolution plus health checks lets callers reach a healthy instance without reconfiguration, and it feeds Traefik's routing.
- **Alternative considered:** Static configuration or DNS-only discovery — rejected; static addresses break on every reschedule and lack health awareness.

**Resilience via `tenacity` (timeout + bounded retry + fallback) on every client:**
- **Decision:** Wrap client calls with an explicit timeout, `tenacity` exponential-backoff retries capped at a small attempt count, and a defined fallback when retries are exhausted.
- **Rationale:** Network calls fail in ways in-process calls do not; bounding time and attempts and defining a fallback keeps a single dependency's fault from cascading into a request-wide failure.
- **Alternative considered:** A full circuit-breaker library with shared trip state — reasonable but heavier than this phase needs; timeout + capped retry + fallback delivers most of the protection, and a breaker can be layered on later if a dependency proves flaky.

**Traefik gateway driven by the Consul catalog, with edge middleware:**
- **Decision:** Front all services with Traefik, route by path prefix using the Consul catalog provider, and enforce auth, logging, and rate limiting as gateway middleware.
- **Rationale:** A single edge gives clients one address and one place to enforce cross-cutting concerns, and catalog-driven routing means new/moved instances are picked up without editing gateway config.
- **Alternative considered:** Client-side routing / no gateway, or Kong instead of Traefik — a gateway is needed to centralize edge concerns; Traefik is chosen for its native Consul-catalog integration and lightweight config, matching the plan.

## Risks / Trade-offs

- **The monolith modules may not yet be materialized in code** → This phase establishes the per-service projects from the plan's module structure; extraction stays faithful to each module's entities/repositories/services/routers so behavior is preserved as services come online.
- **Network calls introduce partial failure where in-process calls could not fail** → Mitigated by the resilience layer (timeout + bounded retry + fallback); list/aggregate paths degrade gracefully rather than failing whole requests.
- **Added latency from synchronous cross-service hops** → Keep the dependency graph shallow (the declared direction avoids cycles), set tight timeouts, and prefer a single hop per read; deeper aggregation moves to later phases if needed.
- **Data duplication / consistency across services** → Each context owns its data and others fetch it live; where a service caches upstream data, it is treated as a cache with its own staleness budget, not a second source of truth.
- **Operational surface grows (multiple services, Consul, Traefik)** → Standardize the per-service blueprint (config, `/health`, Dockerfile, Consul registration) so every service is operated the same way, and stand up Consul and Traefik once in the compose stack.
- **Split-brain during rollout** → Extract behind the gateway one service at a time and keep the monolith serving un-extracted contexts until each service is verified, so traffic shifts incrementally.

## Migration Plan

1. Identify and document the bounded contexts and dependency graph in `docs/bounded-contexts.md`.
2. Stand up the shared infrastructure: add Consul and Traefik to the compose stack and confirm the Consul UI and gateway are reachable.
3. Extract the Auth service (its own project, config, database, Dockerfile, `/health`, Consul registration); verify it registers, passes health checks, and serves through the gateway in isolation.
4. Extract Clients, then Contracts, then Financial in dependency order, adding the required `httpx` clients (`AuthClient`, `ClientClient`, `ContractClient`) with resilience and verifying each against its upstreams.
5. Extract Audit and point it at the existing event bus; verify it consumes events independently of the synchronous services.
6. Configure Traefik path-prefix routing and global middleware (auth, logging, rate limiting) and verify end-to-end routing through the gateway.
7. Rollback: because services are added incrementally behind the gateway while the monolith still serves un-extracted contexts, an extraction can be rolled back by routing its prefix back to the monolith and removing the service, without data migration.

## Open Questions

- What is the per-dependency timeout and retry budget (attempts, backoff bounds)? The plan uses three attempts with exponential backoff; concrete values per client to be tuned once real latencies are observed.
- Does authentication belong solely at the Traefik edge, or should each service also validate tokens defense-in-depth? (Current lean: validate at the edge now, revisit per-service validation when service-to-service auth is added.)
- How is each service's database provisioned and migrated independently — one Postgres instance with a schema per service, or a database per service? (Deferred to the infrastructure setup; the requirement is only that no service reads another's tables.)
- Should a full circuit breaker with shared trip state be introduced now or deferred until a dependency demonstrates instability? (Current lean: defer; timeout + retry + fallback first.)
- Are Negotiations, Notifications, and Reports extracted next phase, or does Reports stay a composition/aggregation service given it depends on every context?
