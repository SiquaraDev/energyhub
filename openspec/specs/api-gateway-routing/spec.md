# api-gateway-routing Specification

## Purpose
TBD - created by archiving change implement-fase-15. Update Purpose after archive.
## Requirements
### Requirement: A single gateway fronts all services

The system SHALL run a Traefik API gateway as the single external entry point, so clients reach services through the gateway rather than by addressing service ports directly.

#### Scenario: External requests enter through the gateway

- **WHEN** an external client sends a request to the platform
- **THEN** it is received by the Traefik gateway, which forwards it to the appropriate service

### Requirement: Requests are routed by path prefix

The gateway SHALL route each incoming request to the owning service based on its path prefix (for example `/api/v1/auth` to the Auth service) using service definitions discovered through the Consul catalog.

#### Scenario: Path prefix selects the service

- **WHEN** a request arrives with a path under `/api/v1/auth`
- **THEN** the gateway forwards it to the Auth service, and a path under a different service's prefix is forwarded to that service

#### Scenario: Routes follow the discovery catalog

- **WHEN** a service is registered in the Consul catalog with its routing rule
- **THEN** the gateway picks up its route from the catalog without a hard-coded backend address

### Requirement: Global edge concerns are enforced at the gateway

The gateway SHALL apply cross-cutting concerns — authentication, request logging, and rate limiting — at the edge so each service is relieved of duplicating them.

#### Scenario: Requests are logged and rate limited at the edge

- **WHEN** requests pass through the gateway
- **THEN** they are logged and subject to the configured rate limit before reaching a service

#### Scenario: Unauthenticated requests are rejected at the edge

- **WHEN** a request to a protected route arrives without valid authentication
- **THEN** the gateway rejects it before it reaches the target service

