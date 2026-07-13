# configuration-and-secrets Specification

## Purpose
TBD - created by archiving change implement-fase-16. Update Purpose after archive.
## Requirements
### Requirement: Dedicated namespace

The system SHALL define an `energyhub` `Namespace` and all platform resources (deployments, services, config, secrets, ingress, autoscalers) MUST be created within it to isolate the platform from other cluster workloads.

#### Scenario: Resources created in the namespace

- **WHEN** the platform manifests are applied
- **THEN** the `energyhub` namespace exists and every platform resource is created inside it

### Requirement: ConfigMaps for non-sensitive configuration

The system SHALL provide a shared `ConfigMap` and per-service `ConfigMap`s carrying non-sensitive configuration (service URLs, ports, environment, Consul host/port), and workloads MUST consume these values via environment variables or mounted config volumes rather than hardcoding them in images.

#### Scenario: Configuration injected as environment variables

- **WHEN** a `Deployment` references a `ConfigMap` key via `valueFrom.configMapKeyRef`
- **THEN** the corresponding value is injected into the container environment at pod start

#### Scenario: Configuration mounted as a volume

- **WHEN** a `ConfigMap` is mounted into a pod at a config path
- **THEN** the configuration file is available to the service at that mount path

### Requirement: Secrets for sensitive values

The system SHALL store sensitive values (database password, RabbitMQ password, JWT/`SECRET_KEY`) in Kubernetes `Secret` objects, and workloads MUST consume them via `valueFrom.secretKeyRef` so sensitive data is never embedded in `Deployment` manifests or images. The committed representation of these secrets MUST NOT contain plaintext secret material: it MUST be encrypted (a `SealedSecret` decrypted in-cluster) or externalized (an `ExternalSecret` referencing a secret manager), and the resolved `Secret` keys MUST match what workloads reference so consumers remain unchanged.

#### Scenario: Secret injected without exposure in manifests

- **WHEN** a container references a `Secret` key via `valueFrom.secretKeyRef`
- **THEN** the secret value is injected into the container environment and does not appear in the `Deployment` manifest

#### Scenario: Sensitive values are separated from ConfigMaps

- **WHEN** configuration is authored for a service
- **THEN** sensitive values are placed in `Secret` objects and non-sensitive values in `ConfigMap`s

#### Scenario: Committed secret artifact contains no plaintext

- **WHEN** the committed secret manifest is inspected in the repository
- **THEN** it is an encrypted `SealedSecret` or an `ExternalSecret` reference and exposes no plaintext credential values

### Requirement: Secret material is produced by a secret manager

The resolved Kubernetes `Secret` SHALL be produced in-cluster by a secret-management mechanism — a Sealed Secrets controller decrypting a committed `SealedSecret`, or an External Secrets Operator resolving an `ExternalSecret` from a store such as HashiCorp Vault — rather than by applying a hand-committed plaintext `Secret`.

#### Scenario: Controller materializes the secret in-cluster

- **WHEN** the committed sealed/external secret is applied to the cluster
- **THEN** the controller resolves it into a Kubernetes `Secret` whose keys match the workloads' `secretKeyRef` references

### Requirement: CI rejects committed plaintext secrets

The system SHALL guard against committing plaintext secret material by failing continuous integration when a plaintext Kubernetes `Secret` or a known placeholder credential value is detected in the repository.

#### Scenario: Plaintext secret fails the pipeline

- **WHEN** a commit introduces a plaintext `Secret` manifest or a known placeholder credential value
- **THEN** the CI guard fails the pipeline and blocks the change

