## MODIFIED Requirements

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
