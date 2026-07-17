## Why

Fase 16 authored the Kubernetes manifests and Fase 17 automated the deploy, but the resulting deployment is validated locally rather than production-robust: images are pinned at deploy time by an imperative `kubectl set image` hack (the base manifests still say `:latest`), Kafka runs alongside a separate Zookeeper as a `Deployment` with no ordered or persistent guarantees, and every stateful backend uses `emptyDir` so its data is lost on any pod restart or reschedule. This change hardens those three weak points — declarative image pinning through Kustomize, Kafka as a KRaft `StatefulSet`, and PersistentVolumeClaims for the stateful backends — so the cluster's desired state is reproducible and its data durable.

## What Changes

- Introduce a **Kustomize base** under `k8s/base/` that aggregates the existing manifests and declares an `images:` transformer entry per service, so image name and tag are managed declaratively in one place instead of being hard-coded as `:latest` in each Deployment.
- Pin each service image to the **commit SHA** through the Kustomize `images:` transformer (`newTag`), replacing the imperative `kubectl -n energyhub set image deployment/<svc>-service ...:${SHA}` step in `deploy.yml`. This resolves the Fase 17 open question about pinning deploy manifests to the SHA tag rather than relying on `latest`.
- Add **environment overlays** under `k8s/overlays/dev/` and `k8s/overlays/prod/` that reference the base and apply environment-specific patches (replica counts, resource sizing, ConfigMap values, and storage class), so `dev` and `prod` diverge without forking the base.
- Migrate the **Kafka workload to KRaft mode as a `StatefulSet`**: drop the Zookeeper `Deployment` and the `KAFKA_ZOOKEEPER_CONNECT` coupling, run a single combined broker+controller node with a self-managed metadata quorum, and back it with a headless `Service` for a stable network identity and ordered lifecycle.
- Replace **`emptyDir` with PersistentVolumeClaims** for the stateful backends — at minimum Postgres (`/var/lib/postgresql/data`) and Kafka (`/var/lib/kafka/data`), extendable to Redis and RabbitMQ — so their data survives pod restart and rescheduling.
- Update the **deploy workflow** so `deploy.yml` renders the target overlay through Kustomize (`kubectl apply -k` / `kustomize build`) with the SHA already injected, dropping the `kubectl set image` and raw `kubectl apply -f k8s/` steps.

## Capabilities

### New Capabilities

- `kustomize-image-pinning`: A Kustomize base whose `images:` transformer pins every service image to an explicit name and commit-SHA tag declaratively, so the deployed image is reproducible from the manifest set and no imperative `kubectl set image` is required.
- `kustomize-environment-overlays`: A Kustomize base plus `dev` and `prod` overlays that apply environment-specific patches on top of the shared base, so each environment is rendered from one source of truth.

### Modified Capabilities

- `data-persistence-volumes`: Extends the persistence guarantee to the Kubernetes deployment — the "data survives a restart cycle" requirement now also covers pod restart/reschedule, and a new requirement mandates PersistentVolumeClaims (replacing `emptyDir`) for the in-cluster stateful backends.
- `messaging-and-streaming-containers`: The containerized-Kafka requirement changes from "Kafka with Zookeeper" to a KRaft-mode broker run as a `StatefulSet` with a stable identity and persistent log storage, dropping the Zookeeper dependency.
- `kubernetes-deploy-automation`: The "manifests applied to the cluster" requirement changes from raw `kubectl apply -f k8s/` plus imperative `kubectl set image` pinning to a Kustomize overlay build with the commit SHA injected declaratively.

## Impact

- **Dependencies**: Adds Kustomize (bundled with modern `kubectl` as `kubectl apply -k`, or the standalone `kustomize` binary). No application runtime dependency changes. The Kafka image (`confluentinc/cp-kafka`) is retained but reconfigured for KRaft; the `confluentinc/cp-zookeeper` image is removed from the deployment.
- **Consumes**: All Fase 16 `k8s/` manifests (Deployments, `kafka.yaml`/`zookeeper.yaml`, `postgres.yaml`/`redis.yaml`/`rabbitmq.yaml`, `ingress.yaml`, ConfigMaps/Secret), and the Fase 17 `deploy.yml` deploy workflow whose imperative image-pinning step this change makes declarative.
- **Provides**: A reproducible, overlay-structured manifest set with SHA-pinned images, a Zookeeper-free KRaft Kafka `StatefulSet`, and durable PVC-backed storage for the stateful backends.
- **New artifacts**: `k8s/base/kustomization.yaml`, `k8s/overlays/dev/kustomization.yaml`, `k8s/overlays/prod/kustomization.yaml` (plus per-overlay patches), a Kafka `StatefulSet` + headless `Service` (replacing `kafka.yaml`/`zookeeper.yaml`), and `PersistentVolumeClaim`/`volumeClaimTemplates` definitions for the stateful backends.
- **Coordination**: The `StorageClass` referenced by the PVCs must exist in the target cluster (the local minikube/kind default `standard` in `dev`; a real class in `prod`); the KRaft cluster requires a formatted `CLUSTER_ID`; and the Fase 17 `deploy.yml` must switch to the Kustomize-based apply so the pinned images take effect.
