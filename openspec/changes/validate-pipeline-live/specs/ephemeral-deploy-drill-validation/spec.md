## ADDED Requirements

### Requirement: Ephemeral kind deploy stage passes end to end

The combined pipeline's `deploy` job SHALL create an ephemeral kind cluster on the runner, load the freshly published SHA-tagged service images, apply the `k8s/` manifests, and conclude green after the core stack becomes ready.

#### Scenario: Kind deploy stage concludes green

- **WHEN** the `deploy` job runs after `build-and-push` succeeds
- **THEN** the kind cluster is created, the service images are loaded, the manifests are applied, and the job finishes with conclusion `success`

#### Scenario: Published images are loaded into kind under expected names

- **WHEN** the image-load step runs
- **THEN** each `ghcr.io/siquaradev/energyhub-<svc>-service:<sha>` image is pulled, retagged to `energyhub-<svc>-service:latest`, and loaded into the `energyhub` kind cluster

### Requirement: All manifests pass server-side dry-run before apply

The `deploy` job SHALL run a server-side dry-run (`kubectl apply --dry-run=server`) over all `k8s/` manifests against the live cluster API before applying them for real.

#### Scenario: Dry-run validates every manifest

- **WHEN** the server-side dry-run step runs
- **THEN** every manifest under `k8s/` passes schema and admission validation against the cluster API with no error

### Requirement: Core stack reaches readiness within the gate timeout

After applying the manifests and scaling services to a single replica, the `deploy` job SHALL wait for the core subset (Postgres, Redis, RabbitMQ, Consul, `auth-service`, `client-service`) to become available within the configured timeouts.

#### Scenario: Core deployments become available

- **WHEN** the readiness gate runs
- **THEN** the Postgres, Redis, RabbitMQ, and Consul deployments and the `auth-service` and `client-service` deployments report `condition=available` before their timeouts elapse

### Requirement: Rollback drill proves self-healing

The `deploy` job SHALL execute a rollback drill: inject a deliberately bad image into a deployment, confirm the rollout does NOT complete within the timeout, run `kubectl rollout undo`, and confirm the deployment recovers to a healthy rollout.

#### Scenario: Bad image fails the rollout and undo recovers it

- **WHEN** an inexistent image is set on `auth-service` and its rollout is observed
- **THEN** the rollout does not complete within the timeout, `rollout undo` is executed, and the subsequent `rollout status` confirms the deployment recovered

#### Scenario: A completing bad rollout is treated as a drill failure

- **WHEN** the injected bad-image rollout unexpectedly completes within the timeout
- **THEN** the drill step fails the job (the self-healing mechanism is not proven), rather than passing silently
