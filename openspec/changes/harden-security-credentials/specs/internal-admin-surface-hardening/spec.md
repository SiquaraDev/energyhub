## ADDED Requirements

### Requirement: Internal endpoints require an inter-service credential

The `/internal/*` endpoints SHALL require a valid inter-service credential (for example a shared secret header or token) on every request, and MUST reject unauthenticated calls, rather than relying solely on not being routed by the public gateway.

#### Scenario: Unauthenticated internal call is rejected

- **WHEN** a client calls an `/internal/*` endpoint (for example `GET /internal/users/{id}`) without the inter-service credential
- **THEN** the request is rejected with an unauthorized response and no user data is returned

#### Scenario: Authenticated inter-service call succeeds

- **WHEN** a calling service invokes an `/internal/*` endpoint with a valid inter-service credential
- **THEN** the request is processed and the expected response is returned

### Requirement: Internal endpoints are never publicly exposed

The `/internal/*` endpoints SHALL NOT be reachable through the public gateway or `Ingress`, and network policy MUST restrict them to the services that need them.

#### Scenario: Internal path is not routed at the edge

- **WHEN** an external client requests an `/internal/*` path through the public edge
- **THEN** the request is not routed to the internal endpoint

### Requirement: Traefik dashboard is secured

The Traefik dashboard SHALL NOT run in insecure mode and MUST require authentication, and it MUST NOT be exposed on the public edge.

#### Scenario: Insecure dashboard mode is disabled

- **WHEN** the Traefik configuration is inspected
- **THEN** `insecure` is not enabled and the dashboard is protected by an authentication middleware

#### Scenario: Unauthenticated dashboard access is denied

- **WHEN** a client attempts to open the Traefik dashboard without valid credentials
- **THEN** access is denied

### Requirement: Consul UI is access-controlled and internal

The Consul UI SHALL NOT be publicly exposed, and access to the Consul HTTP interface MUST be restricted to authorized workloads by network policy (and access control where available).

#### Scenario: Consul UI is not reachable externally

- **WHEN** an external client attempts to reach the Consul UI through the public edge
- **THEN** the request is not routed and the UI is not accessible externally

#### Scenario: Only authorized workloads reach Consul

- **WHEN** a pod that is not a registered service or scraper attempts to reach the Consul HTTP port
- **THEN** the connection is denied by network policy
