## ADDED Requirements

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

The deploy job SHALL apply the Kubernetes manifests from the `k8s/` directory (namespace, config, secrets, and workload manifests) to the cluster.

#### Scenario: All manifests are applied

- **WHEN** the deploy step runs
- **THEN** the `k8s/` manifests are applied so the cluster's desired state matches the repository

### Requirement: Rollout verification

After applying manifests, the deploy job SHALL verify the rollout status of the platform Deployments (e.g. `auth-service`, `client-service`, `api-gateway`) and SHALL fail if a rollout does not complete.

#### Scenario: Rollout status is checked

- **WHEN** the manifests have been applied
- **THEN** the job runs `kubectl rollout status` for the key Deployments and fails if any rollout does not succeed
