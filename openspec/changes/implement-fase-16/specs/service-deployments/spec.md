## ADDED Requirements

### Requirement: Deployment per microservice

The system SHALL declare a Kubernetes `Deployment` for each microservice (auth, client, contract, financial, audit) and platform component (Consul, Traefik/gateway) in the `energyhub` namespace, each referencing the service container image and its container port.

#### Scenario: Deployment schedules the service pods

- **WHEN** a service `Deployment` manifest is applied to the cluster
- **THEN** the scheduler creates pods running the specified image on the declared container port within the `energyhub` namespace

#### Scenario: Every service has a deployment

- **WHEN** the `k8s/` manifests are enumerated
- **THEN** each microservice and platform component has a corresponding `Deployment` manifest

### Requirement: Declared replica count

Each `Deployment` MUST declare a `replicas` count so the desired number of pod instances is maintained, and the control plane MUST recreate a replacement pod when a pod terminates.

#### Scenario: Desired replica count is maintained

- **WHEN** a `Deployment` declares `replicas: 2` and one of its pods is deleted or crashes
- **THEN** the control plane schedules a replacement pod to restore the desired count of 2

### Requirement: Resource requests and limits

Each service container MUST declare `resources.requests` and `resources.limits` for CPU and memory so pods are schedulable against node capacity and constrained from exhausting node resources.

#### Scenario: Pod scheduled against declared requests

- **WHEN** a pod with declared CPU/memory requests is scheduled
- **THEN** it is placed only on a node with sufficient allocatable capacity, and its usage is capped by the declared limits

### Requirement: Liveness and readiness probes

Each service container MUST define a `livenessProbe` and a `readinessProbe` that call the service `/health` endpoint on its container port, so unhealthy pods are restarted and traffic is only routed to ready pods.

#### Scenario: Unhealthy pod is restarted

- **WHEN** a pod's `livenessProbe` against `/health` fails repeatedly
- **THEN** the kubelet restarts the container

#### Scenario: Traffic withheld until readiness passes

- **WHEN** a pod is starting and its `readinessProbe` against `/health` has not yet succeeded
- **THEN** the pod is excluded from its Service endpoints and receives no traffic until the probe succeeds
