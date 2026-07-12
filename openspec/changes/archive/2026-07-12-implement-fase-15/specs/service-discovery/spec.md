## ADDED Requirements

### Requirement: Services register themselves with Consul on startup

Each service SHALL register itself with Consul at startup under its logical `app_name` and a unique service id, supplying its address and port, so it becomes discoverable by name.

#### Scenario: Service appears in the catalog after startup

- **WHEN** a service completes its startup sequence
- **THEN** it is present in the Consul catalog under its `app_name` with its address and port

#### Scenario: Unique service id per instance

- **WHEN** a service registers
- **THEN** it registers with a service id derived from its name and port so multiple instances do not collide

### Requirement: Registration includes an HTTP health check

Each Consul registration SHALL declare an HTTP health check against the service's `/health` endpoint on a defined interval, so Consul reflects the current health of each instance.

#### Scenario: Unhealthy instance is marked failing

- **WHEN** a registered instance stops responding on `/health`
- **THEN** Consul marks that instance's health check as failing within the configured interval

#### Scenario: Healthy instance passes its check

- **WHEN** a registered instance responds successfully on `/health`
- **THEN** Consul reports its health check as passing

### Requirement: Services are located by logical name

The system SHALL resolve a dependency's network location through Consul by logical service name rather than a hard-coded host and port, so instances can move without reconfiguring callers.

#### Scenario: Caller resolves a dependency by name

- **WHEN** a service needs to call another service
- **THEN** it obtains a healthy instance's address by looking up the target's logical name rather than relying on a static address
