# cluster-image-pull-authentication Specification

## Purpose
TBD - created by archiving change harden-cicd-supply-chain. Update Purpose after archive.
## Requirements
### Requirement: GHCR image-pull secret in the namespace

The change SHALL provide a Kubernetes secret of type `kubernetes.io/dockerconfigjson` in the `energyhub` namespace that holds credentials for `ghcr.io`, so that the cluster can authenticate when pulling the private service images published under `ghcr.io/siquaradev/...`.

#### Scenario: Pull secret exists for GHCR

- **WHEN** the platform manifests are applied to the cluster
- **THEN** a `kubernetes.io/dockerconfigjson` secret targeting the `ghcr.io` registry exists in the `energyhub` namespace

### Requirement: Service workloads reference the image-pull secret

The service Deployments SHALL be able to pull the private GHCR images by referencing the image-pull secret, either through each Deployment's pod `imagePullSecrets` or through the namespace ServiceAccount used by the service pods.

#### Scenario: Private image is pulled successfully

- **WHEN** a service Deployment references a private `ghcr.io/siquaradev/energyhub-<service>-service` image and the pull secret is wired in
- **THEN** the kubelet authenticates to GHCR and pulls the image instead of failing with `ImagePullBackOff`

#### Scenario: Wiring covers every service workload

- **WHEN** the service Deployments (auth, client, contract, financial, audit) are inspected
- **THEN** each one resolves an `imagePullSecrets` reference to the GHCR pull secret, directly or via its ServiceAccount

### Requirement: Credentials sourced only from secrets

The `dockerconfigjson` contents SHALL be built from a GHCR access token supplied as a secret (the workflow `GITHUB_TOKEN` or a `read:packages` personal access token) and SHALL NOT be committed to the repository in plaintext.

#### Scenario: No plaintext registry credentials in the repository

- **WHEN** the repository and manifests are inspected
- **THEN** no plaintext GHCR password or token appears, and the pull secret is materialized from a secret-provided credential

### Requirement: Documented public-package alternative

The change SHALL document making the GHCR packages public as an alternative to the pull secret, describing the trade-off (public images need no pull secret but are world-readable) so operators can choose per environment.

#### Scenario: Alternative is documented

- **WHEN** an operator reads the image-pull documentation
- **THEN** it explains both approaches — a `dockerconfigjson` pull secret for private packages and publishing the packages public — and when to use each

