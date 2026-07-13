## ADDED Requirements

### Requirement: Kustomize base plus environment overlays

The system SHALL provide a Kustomize base at `k8s/base/` and per-environment overlays at `k8s/overlays/dev/` and `k8s/overlays/prod/`, where each overlay references the base (`resources: [../../base]`) and applies only environment-specific patches, so the base remains the single source of structure for the `energyhub` platform.

#### Scenario: Overlay references the shared base

- **WHEN** an overlay `kustomization.yaml` is inspected
- **THEN** it lists the shared base under `resources` and contains only the patches, config, and image tags specific to that environment

#### Scenario: Both overlays build cleanly

- **WHEN** `kustomize build k8s/overlays/dev` and `kustomize build k8s/overlays/prod` are run
- **THEN** each renders the complete `energyhub` resource set without error

### Requirement: Overlays apply environment-specific configuration

Each overlay SHALL customize environment-specific values — at minimum replica counts, resource requests/limits, ConfigMap values, image tags, and the persistence `StorageClass` — through patches layered on the base rather than by duplicating base manifests.

#### Scenario: Dev and prod diverge without forking the base

- **WHEN** the `dev` and `prod` overlays are built
- **THEN** the rendered manifests differ only in the patched environment-specific fields while sharing the same underlying base resources

#### Scenario: Prod overlay sets an explicit storage class

- **WHEN** the `prod` overlay is built
- **THEN** the stateful backends' PersistentVolumeClaims reference the storage class declared by the `prod` overlay rather than relying on an implicit default

### Requirement: An overlay renders the full deployable manifest set

Building any environment overlay SHALL produce the full set of resources needed to deploy the platform to that environment, so a deploy can apply a single overlay with `kubectl apply -k k8s/overlays/<env>`.

#### Scenario: Building an overlay yields a deployable set

- **WHEN** `kubectl apply -k k8s/overlays/dev` is run against a cluster
- **THEN** the namespace, config, secrets, service workloads, stateful backends, gateway, and ingress for the `dev` environment are all applied
