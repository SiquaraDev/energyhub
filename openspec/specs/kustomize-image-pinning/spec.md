# kustomize-image-pinning Specification

## Purpose
TBD - created by archiving change k8s-production-robustness. Update Purpose after archive.
## Requirements
### Requirement: Kustomize base declares service images

The system SHALL provide a Kustomize base at `k8s/base/kustomization.yaml` that aggregates the platform's workload manifests and declares an `images:` transformer entry for each service (`auth`, `client`, `contract`, `financial`, `audit`, and the gateway), so every service image reference is managed declaratively in one place rather than hard-coded in each Deployment.

#### Scenario: Base renders with managed image references

- **WHEN** `kustomize build k8s/base` is run
- **THEN** the rendered manifest set is produced and each service Deployment's image is taken from the base `images:` transformer rather than an inline `:latest` literal

#### Scenario: Every service has a transformer entry

- **WHEN** the base `images:` list is enumerated
- **THEN** there is exactly one entry per platform service, keyed by the service image name

### Requirement: Service images are pinned to the commit SHA

The system SHALL pin each service image to an explicit registry name and the immutable commit-SHA tag through the Kustomize `images:` transformer (`newName` + `newTag`), so the deployed image is reproducible from the manifest set alone.

#### Scenario: Transformer sets the SHA tag

- **WHEN** the image tag is set for a release (e.g. via `kustomize edit set image energyhub-auth-service=ghcr.io/<owner>/energyhub-auth-service:<sha>`) and the overlay is built
- **THEN** the rendered Deployment references `ghcr.io/<owner>/energyhub-auth-service:<sha>` with the commit SHA as the tag

#### Scenario: Rendered image is inspectable without applying

- **WHEN** an operator runs `kustomize build` for the target overlay
- **THEN** the exact image and SHA that a deploy will run is visible in the rendered output before anything is applied to the cluster

### Requirement: No imperative image mutation

The deployment SHALL NOT rely on an imperative `kubectl set image` step to select the running image; the image pin MUST come entirely from the Kustomize `images:` transformer, and the base Deployment manifests MUST reference a stable image name that the transformer overrides.

#### Scenario: Deploy applies pinned images declaratively

- **WHEN** the deploy applies the built overlay with `kubectl apply -k`
- **THEN** the pods run the SHA-tagged images from the transformer and no `kubectl set image` command is issued

#### Scenario: Base manifests carry no environment-specific tag

- **WHEN** a base Deployment manifest is inspected
- **THEN** its image field is a stable placeholder name (no `:latest` deploy-time tag), and the concrete registry name and SHA tag are supplied only by the transformer

