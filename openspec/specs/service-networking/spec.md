# service-networking Specification

## Purpose
TBD - created by archiving change implement-fase-16. Update Purpose after archive.
## Requirements
### Requirement: Internal service exposure via ClusterIP

The system SHALL define a `ClusterIP` `Service` for each internal microservice, selecting its pods by label and exposing its container port, so other services can reach it over a stable in-cluster DNS name.

#### Scenario: Service reachable by DNS name

- **WHEN** a pod issues a request to another service by its `Service` name (e.g. `http://client-service:8002/health`)
- **THEN** the request is resolved via cluster DNS and load-balanced to a ready pod behind that `Service`

#### Scenario: Service targets pods by selector

- **WHEN** a `Service` declares a label selector matching a `Deployment`'s pod labels
- **THEN** only pods matching that selector are added to the `Service` endpoints

### Requirement: Edge exposure via LoadBalancer

The system SHALL expose the gateway (Traefik) through a `LoadBalancer` `Service` so external clients can reach the platform through a single edge endpoint.

#### Scenario: Gateway exposed externally

- **WHEN** the gateway `LoadBalancer` `Service` is applied
- **THEN** an external address is provisioned that forwards to the gateway pods on the declared ports

### Requirement: Stable endpoints across pod churn

Service endpoints MUST reflect only ready pods, so traffic continues to reach healthy replicas as pods are rescheduled, scaled, or restarted.

#### Scenario: Endpoints follow ready pods

- **WHEN** a pod behind a `Service` is replaced or a new replica becomes ready
- **THEN** the `Service` endpoints are updated to include ready pods and exclude terminated ones without changing the `Service` DNS name

