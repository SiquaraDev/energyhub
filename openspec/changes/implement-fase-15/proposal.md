## Why

Fase 14 stabilized the modular monolith, but every module still ships, scales, and fails as a single unit — a change to reports forces a redeploy of auth, and one hot module drags the whole process. This phase splits the monolith along its bounded contexts into independently deployable FastAPI services so each context can evolve, scale, and be released on its own, communicating over the network through service discovery and an API gateway.

## What Changes

- Identify the bounded contexts hidden in the existing modules (Auth, Clients, Contracts, Negotiations, Financial, Audit, Notifications, Reports), map their dependency graph, and document the target services in `docs/bounded-contexts.md`.
- Extract Auth, Clients, Contracts, Financial, and Audit each into a standalone FastAPI project under `services/<name>-service/` with its own `pyproject.toml`, config, database, `Dockerfile`, and `/health` endpoint, carrying over the module's entities, repositories, services, routers, DTOs, and mappers.
- Add Consul-based service discovery: each service registers itself on startup with an HTTP health check and is discoverable by logical name rather than a hard-coded host/port.
- Add synchronous inter-service communication via `httpx` clients (e.g. `AuthClient`, `ClientClient`, `ContractClient`) that replace the in-process calls a module previously made to another module.
- Add resilience policies on those clients — bounded timeouts, `tenacity` retries with exponential backoff, and fallback behavior — so a slow or unavailable dependency degrades gracefully instead of cascading.
- Add a Traefik API gateway that routes external requests to services by path prefix (via the Consul catalog) and applies global concerns (authentication, logging, rate limiting) at the edge.
- **BREAKING**: The single-process HTTP entry point is replaced by per-service entry points reached through the gateway; cross-module calls become network calls and each service owns its own database.

## Capabilities

### New Capabilities

- `bounded-context-decomposition`: Analysis and documentation of the bounded contexts, their ownership boundaries, and the inter-context dependency graph that drives the split.
- `service-extraction`: A repeatable blueprint that turns a module into an independently deployable FastAPI service with its own project, configuration, database, container image, and health endpoint.
- `service-discovery`: Consul-based registration with HTTP health checks and name-based lookup so services locate each other without hard-coded addresses.
- `inter-service-communication`: `httpx`-based clients that expose a typed API for one service to call another, replacing former in-process module calls.
- `service-resilience`: Timeout, retry-with-backoff, circuit-breaking, and fallback policies applied to inter-service calls so dependency failures stay contained.
- `api-gateway-routing`: A Traefik gateway that routes external traffic to services by path prefix and enforces global edge concerns (auth, logging, rate limiting).

### Modified Capabilities

None — this phase introduces the microservices topology; no previously specified requirements change.

## Impact

- **Dependencies**: Adds `httpx`, a Consul client (`python-consul`), and `tenacity` to each extracted service; introduces the Consul and Traefik container images to the compose stack.
- **Consumes**: The stable modular monolith from Fase 14, the containerized environment (Fase 12+), and the existing event bus (RabbitMQ/Kafka) that the Audit service continues to consume.
- **Provides**: `services/auth-service/`, `services/client-service/`, `services/contract-service/`, `services/financial-service/`, and `services/audit-service/` as standalone deployables, the Consul discovery layer, the HTTP client + resilience layer, and the Traefik gateway routing configuration.
- **New artifacts**: `docs/bounded-contexts.md`; per-service `pyproject.toml`, `energyhub/config.py`, `energyhub/main.py` (Consul registration), and `Dockerfile`; `traefik/traefik.yml` and gateway compose definitions; Consul compose definition.
- **Coordination**: Each service owns its own database/schema (data is no longer shared in-process); the dependency direction (Clients→Auth, Contracts→Auth+Clients, Financial→Auth+Clients+Contracts, Audit independent) is preserved via HTTP clients rather than imports.
