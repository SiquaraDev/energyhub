## MODIFIED Requirements

### Requirement: Services register themselves with Consul on startup

Each service SHALL register itself with Consul at startup under its logical `app_name` and a service id that is unique per running instance, supplying its address and port, so it becomes discoverable by name. The unique instance id SHALL be derived from the service name and a per-instance discriminator — the Kubernetes pod `HOSTNAME` when present, otherwise a per-process UUID — and SHALL be sent as the Consul registration `ID`, while the logical `Name` remains the `app_name`, so name-based discovery and catalog routing are unaffected.

#### Scenario: Service appears in the catalog after startup

- **WHEN** a service completes its startup sequence
- **THEN** it is present in the Consul catalog under its `app_name` with its address and port

#### Scenario: Unique service id per instance

- **WHEN** a service instance registers
- **THEN** it registers with a service id derived from its name and a per-instance discriminator (the pod `HOSTNAME`, or a per-process UUID when `HOSTNAME` is unavailable) so that two instances never share the same id

#### Scenario: Replicas coexist in the catalog without overwriting each other

- **WHEN** a Deployment runs more than one replica (for example after the HPA scales out) and each replica registers
- **THEN** each replica appears as its own catalog entry under the shared `app_name` and no replica's registration overwrites or replaces another's

## ADDED Requirements

### Requirement: Each instance deregisters only its own registration on shutdown

Each service instance SHALL deregister exactly the unique service id it registered with when it shuts down, so a stopping or rescheduled replica removes only its own catalog entry and never a sibling replica's registration.

#### Scenario: Instance removes only its own entry on shutdown

- **WHEN** a service instance completes its shutdown sequence
- **THEN** it deregisters its own unique service id from Consul and leaves every sibling instance's registration in place

#### Scenario: Sibling replicas remain discoverable after one instance stops

- **WHEN** one replica of a multi-replica Deployment stops and deregisters
- **THEN** the remaining replicas stay present in the Consul catalog under the shared `app_name` and continue to be resolvable by name
