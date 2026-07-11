## ADDED Requirements

### Requirement: Ingress controller present

The system SHALL provision an ingress controller in the cluster so that `Ingress` resources are reconciled into working external HTTP routing.

#### Scenario: Ingress resources are reconciled

- **WHEN** an ingress controller is running and an `Ingress` resource is applied
- **THEN** the controller programs the routing rules and begins accepting external traffic for the declared host

### Requirement: Host and path routing to the gateway

The system SHALL define an `Ingress` resource in the `energyhub` namespace that routes external HTTP traffic for the platform host to the gateway `Service` by host and path.

#### Scenario: External request routed to the gateway

- **WHEN** an external client requests the platform host (e.g. `http://energyhub.local/health`)
- **THEN** the `Ingress` routes the request to the gateway `Service` and returns the service response

#### Scenario: Local host mapping enables access

- **WHEN** the platform host is mapped to the cluster ingress address (e.g. via `/etc/hosts`)
- **THEN** requests to that host resolve to the ingress and are routed to the gateway
