## ADDED Requirements

### Requirement: Default-deny ingress within the namespace

The system SHALL apply a default-deny ingress `NetworkPolicy` in the `energyhub` namespace so that pod-to-pod traffic is denied unless explicitly allowed.

#### Scenario: Unmatched traffic is denied by default

- **WHEN** a pod attempts to connect to another pod in the namespace for which no allow policy exists
- **THEN** the connection is denied by the default-deny policy

### Requirement: Explicit least-privilege allow rules

The system SHALL define explicit allow `NetworkPolicy` rules that permit only each service's declared dependencies — for example gateway-to-services, services-to-auth `/internal`, services-to-datastores (PostgreSQL, RabbitMQ, Consul), and scraper-to-metrics — so each workload can reach only what it needs.

#### Scenario: Declared dependency is permitted

- **WHEN** a service connects to a dependency for which an explicit allow rule exists (for example a service reaching the auth `/internal` endpoints)
- **THEN** the connection is permitted

#### Scenario: Undeclared connection is blocked

- **WHEN** a service attempts to connect to a peer that is not among its declared dependencies
- **THEN** the connection is blocked because no allow rule matches it

### Requirement: Datastore and control-plane access is restricted

Access to the PostgreSQL, RabbitMQ, and Consul ports SHALL be restricted by `NetworkPolicy` to only the workloads that depend on them.

#### Scenario: Unauthorized pod cannot reach a datastore

- **WHEN** a pod that does not depend on PostgreSQL attempts to open a connection to the PostgreSQL port
- **THEN** the connection is denied by network policy
