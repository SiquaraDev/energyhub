## ADDED Requirements

### Requirement: Metrics source for autoscaling

The system SHALL provision the Metrics Server so that pod CPU and memory utilization are available to the autoscaling control loop.

#### Scenario: Utilization metrics available

- **WHEN** the Metrics Server is running and a `HorizontalPodAutoscaler` queries pod metrics
- **THEN** current CPU and memory utilization for the target `Deployment`'s pods are reported

### Requirement: HorizontalPodAutoscaler per service

The system SHALL define a `HorizontalPodAutoscaler` for each scalable service targeting its `Deployment`, with `minReplicas`, `maxReplicas`, and CPU and memory utilization targets.

#### Scenario: Scale out under load

- **WHEN** average CPU utilization of a `Deployment`'s pods exceeds its configured target
- **THEN** the HPA increases the replica count toward `maxReplicas` while remaining within the declared bounds

#### Scenario: Scale in when idle

- **WHEN** average utilization falls below the configured target for the stabilization window
- **THEN** the HPA decreases the replica count toward `minReplicas` but never below it

### Requirement: Replica bounds are respected

The autoscaler MUST keep the replica count within `[minReplicas, maxReplicas]` at all times regardless of measured load.

#### Scenario: Count clamped to bounds

- **WHEN** measured load would imply a replica count outside the configured range
- **THEN** the effective replica count is clamped to `minReplicas` or `maxReplicas`
