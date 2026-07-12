## 1. Bounded Context Decomposition

- [x] 1.1 Inventory the existing modules (Auth, Clients, Contracts, Negotiations, Financial, Audit, Notifications, Reports) and assign each to exactly one target service
- [x] 1.2 Map the inter-context dependency graph (Auth independent; Clients→Auth; Contracts→Auth+Clients; Negotiations→Auth+Contracts; Financial→Auth+Contracts; Audit/Notifications independent event consumers) and confirm it is acyclic
- [x] 1.3 Derive the extraction order from the dependency graph (Auth first, then Clients, Contracts, Financial, Audit)
- [x] 1.4 Document contexts, responsibilities, and the dependency graph in `docs/bounded-contexts.md`

## 2. Discovery Infrastructure

- [x] 2.1 Add a Consul service to the compose stack (server + UI, on the shared network) with a persistent volume
- [x] 2.2 Start the stack and confirm the Consul UI is reachable at `http://localhost:8500`
- [x] 2.3 Create a reusable Consul registration helper (`register_with_consul`) that registers name, unique service id, address, port, and an HTTP `/health` check

## 3. Auth Service Extraction

- [x] 3.1 Create `services/auth-service/` with its own `pyproject.toml` and dependency set (fastapi, uvicorn, sqlalchemy, asyncpg, alembic, pydantic, python-jose, passlib, python-consul, httpx)
- [x] 3.2 Carry over the auth entities, repositories, services, routers, DTOs, and mappers into the service package
- [x] 3.3 Add `energyhub/config.py` `Settings` with `app_name="auth-service"`, `app_port=8001`, and Consul host/port
- [x] 3.4 Add a `/health` endpoint and register the service with Consul on startup
- [x] 3.5 Add the `Dockerfile` and confirm the image builds and the service starts in isolation
- [x] 3.6 Verify the Auth service registers in Consul and its health check passes

## 4. Client Service Extraction

- [x] 4.1 Create `services/client-service/` with its own `pyproject.toml` (fastapi, uvicorn, sqlalchemy, asyncpg, httpx, python-consul)
- [x] 4.2 Carry over the clients entities, repositories, services, routers, DTOs, and mappers
- [x] 4.3 Add `energyhub/config.py` `Settings` with `app_name="client-service"`, `app_port=8002`, Auth service host/port, and Consul host/port
- [x] 4.4 Implement `AuthClient` (async `httpx`) with `get_user_by_id` and `get_user_by_username`, using `raise_for_status` and a `close` method
- [x] 4.5 Replace the former in-process Auth calls with `AuthClient` calls
- [x] 4.6 Add `/health`, Consul registration, and the `Dockerfile`; verify the service starts and registers

## 5. Contract Service Extraction

- [x] 5.1 Create `services/contract-service/` with its own `pyproject.toml` and carry over the contracts entities, repositories, services, routers, DTOs, and mappers
- [x] 5.2 Add `energyhub/config.py` `Settings` with `app_name="contract-service"`, `app_port=8003`, Auth and Client service host/port, and Consul host/port
- [x] 5.3 Implement `AuthClient` and `ClientClient` HTTP clients and replace the in-process Auth/Clients calls with them
- [x] 5.4 Add `/health`, Consul registration, and the `Dockerfile`; verify the service starts, registers, and reaches its upstreams

## 6. Financial Service Extraction

- [x] 6.1 Create `services/financial-service/` with its own `pyproject.toml` and carry over the financial entities, repositories, services, routers, DTOs, and mappers
- [x] 6.2 Add `energyhub/config.py` `Settings` with `app_name="financial-service"`, `app_port=8004`, Auth/Client/Contract service host/port, and Consul host/port
- [x] 6.3 Implement `AuthClient`, `ClientClient`, and `ContractClient` and replace the in-process cross-module calls with them
- [x] 6.4 Add `/health`, Consul registration, and the `Dockerfile`; verify the service starts, registers, and reaches its upstreams

## 7. Audit Service Extraction

- [x] 7.1 Create `services/audit-service/` with its own `pyproject.toml` and carry over the audit entities, repositories, services, and routers
- [x] 7.2 Add `energyhub/config.py` `Settings` with `app_name="audit-service"`, `app_port=8005`, `rabbitmq_url`, and Consul host/port
- [x] 7.3 Configure the service to consume audit events from the existing RabbitMQ/Kafka bus (no synchronous upstream dependency)
- [x] 7.4 Add `/health`, Consul registration, and the `Dockerfile`; verify the service starts, registers, and consumes events

## 8. Inter-Service Resilience

- [x] 8.1 Apply an explicit `httpx` request timeout to every HTTP client
- [x] 8.2 Add `tenacity` retry (bounded attempts, exponential backoff) to each client method
- [x] 8.3 Define a fallback (e.g. return `None` / safe default) when retries are exhausted so failures do not cascade
- [x] 8.4 Ensure each service closes its HTTP clients on shutdown to release connection pools

## 9. API Gateway Routing

- [x] 9.1 Add a Traefik service to the compose stack with the Docker and Consul-catalog providers enabled
- [x] 9.2 Author `traefik/traefik.yml` with entrypoints and the Consul-catalog provider configuration
- [x] 9.3 Add per-service routing labels/rules mapping path prefixes to services (e.g. `/api/v1/auth` → auth-service)
- [x] 9.4 Configure global edge middleware for authentication, logging, and rate limiting
- [x] 9.5 Verify external requests route through the gateway to the correct service by path prefix

## 10. Validation

- [x] 10.1 Confirm all five services register in Consul and their health checks pass
- [x] 10.2 Confirm cross-service calls succeed through the HTTP clients and preserve the declared dependency direction
- [x] 10.3 Confirm resilience behavior: a downed dependency triggers retries and then the fallback without failing the whole request chain
- [x] 10.4 Confirm the gateway routes each path prefix to its service and enforces auth, logging, and rate limiting at the edge
- [x] 10.5 Run `openspec validate implement-fase-15` and confirm the change is valid
