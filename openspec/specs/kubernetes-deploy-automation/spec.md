# kubernetes-deploy-automation Specification

## Purpose
TBD - created by archiving change implement-fase-17. Update Purpose after archive.
## Requirements
### Requirement: Deploy workflow triggered on main

The system SHALL provide a GitHub Actions workflow at `.github/workflows/deploy.yml` that runs on `push` to `main` and deploys the platform to the Kubernetes cluster.

#### Scenario: Deploy runs only for main

- **WHEN** a commit is pushed to `main`
- **THEN** the deploy workflow is triggered

#### Scenario: Non-main pushes do not deploy

- **WHEN** a commit is pushed to a non-`main` branch
- **THEN** the deploy workflow does not run

### Requirement: kubectl configured from a secret

The deploy job SHALL configure `kubectl` access using a kubeconfig supplied through the `KUBE_CONFIG` GitHub secret, and SHALL NOT store cluster credentials in the repository.

#### Scenario: Cluster context loaded from secret

- **WHEN** the deploy job starts
- **THEN** `kubectl` is configured from the `KUBE_CONFIG` secret and can reach the target cluster

### Requirement: Manifests applied to the cluster

The deploy job SHALL render and apply the platform's Kubernetes manifests through Kustomize — building the target environment overlay (`kubectl apply -k k8s/overlays/<env>`) with each service image already pinned to the commit SHA via the base `images:` transformer — instead of applying raw manifests with `kubectl apply -f k8s/` and pinning images imperatively with `kubectl set image`. The namespace SHALL still be ensured before the namespaced resources.

#### Scenario: Overlay applied via Kustomize

- **WHEN** the deploy step runs
- **THEN** the target overlay is applied with `kubectl apply -k` so the cluster's desired state matches the rendered overlay (namespace, config, secrets, workloads, stateful backends, gateway, and ingress)

#### Scenario: Images pinned declaratively, not imperatively

- **WHEN** the manifests are applied
- **THEN** the deployed workloads run the SHA-tagged images supplied by the Kustomize `images:` transformer, and the job issues no `kubectl set image` command

#### Scenario: Namespace ensured before namespaced resources

- **WHEN** the overlay is applied to a fresh cluster
- **THEN** the `energyhub` namespace exists before the namespaced resources are created, so no resource fails with "namespace not found"

### Requirement: Rollout verification

After applying manifests, the deploy job SHALL verify the rollout status of the platform Deployments (e.g. `auth-service`, `client-service`, `api-gateway`) and SHALL fail if a rollout does not complete.

#### Scenario: Rollout status is checked

- **WHEN** the manifests have been applied
- **THEN** the job runs `kubectl rollout status` for the key Deployments and fails if any rollout does not succeed

