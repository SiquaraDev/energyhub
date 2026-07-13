## ADDED Requirements

### Requirement: Manifests apply cleanly

The system SHALL support applying the full `k8s/` manifest set to the cluster, after which every declared workload MUST reach a `Running` and ready state.

#### Scenario: All pods reach ready

- **WHEN** all manifests under `k8s/` are applied to the cluster
- **THEN** every deployed pod reaches the `Running` phase and passes its readiness probe

### Requirement: Inter-service communication over cluster DNS

The deployed services MUST be able to reach one another by their in-cluster `Service` DNS names, confirming the networking layer works end to end.

#### Scenario: Service-to-service call succeeds

- **WHEN** a request is issued from inside one service pod to another service's health endpoint by DNS name (e.g. `curl http://client-service:8002/health`)
- **THEN** a successful response is returned, confirming DNS resolution and connectivity between pods

### Requirement: End-to-end business flow across the cluster

The platform MUST support the complete business flow through the cluster's edge entry point: authenticate, create a client, create a contract, and record the corresponding audit entry.

#### Scenario: Full flow through the gateway

- **WHEN** a client authenticates through the gateway and then creates a client and a contract
- **THEN** each step succeeds and a corresponding audit record is produced, confirming the distributed deployment is functional end to end
