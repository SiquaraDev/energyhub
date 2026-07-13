## 1. Kustomize Base

- [ ] 1.1 Create `k8s/base/kustomization.yaml` listing the existing workload resources (namespace, ConfigMaps, Secret, per-service Deployments/Services/HPAs, stateful backends, Consul, Traefik, Ingress)
- [ ] 1.2 Move the raw `k8s/*.yaml` workload manifests under `k8s/base/` so the base is the single source of structure
- [ ] 1.3 Add an `images:` transformer to the base with one entry per service (`energyhub-<svc>-service` → `newName: ghcr.io/<owner>/energyhub-<svc>-service`) and a stable placeholder tag
- [ ] 1.4 Confirm `kustomize build k8s/base` renders the full resource set and every service image resolves from the transformer (no inline `:latest`)

## 2. Environment Overlays

- [ ] 2.1 Create `k8s/overlays/dev/kustomization.yaml` referencing the base (`resources: [../../base]`) with dev-only patches (default `StorageClass`, dev replicas/resources, dev ConfigMap values)
- [ ] 2.2 Create `k8s/overlays/prod/kustomization.yaml` referencing the base with prod-only patches (explicit `StorageClass`, prod replicas/resources/limits, prod ConfigMap values)
- [ ] 2.3 Confirm `kustomize build k8s/overlays/dev` and `kustomize build k8s/overlays/prod` each render cleanly and differ only in the patched environment-specific fields

## 3. Kafka as a KRaft StatefulSet

- [ ] 3.1 Author a Kafka `StatefulSet` in KRaft mode (`KAFKA_PROCESS_ROLES=broker,controller`, `KAFKA_NODE_ID`, `KAFKA_CONTROLLER_QUORUM_VOTERS`, `KAFKA_CONTROLLER_LISTENER_NAMES`, formatted `CLUSTER_ID`), dropping `KAFKA_ZOOKEEPER_CONNECT`
- [ ] 3.2 Add a headless `Service` (`kafka-headless`) for stable pod identity and keep the `kafka-service` ClusterIP for clients
- [ ] 3.3 Remove `k8s/zookeeper.yaml` and the Zookeeper `Deployment`/`Service`, and retire the `Recreate` strategy / `broker.id` znode workaround
- [ ] 3.4 Preserve the tuned `KAFKA_HEAP_OPTS`, resource requests/limits, and readiness/liveness probes adapted for KRaft
- [ ] 3.5 Deploy to a scratch cluster and confirm the broker becomes ready and accepts topic operations with Zookeeper removed

## 4. Persistent Storage

- [ ] 4.1 Convert PostgreSQL from `emptyDir` to a PersistentVolumeClaim mounted at `/var/lib/postgresql/data`, preserving `PGDATA=/var/lib/postgresql/data/pgdata` and the initdb ConfigMap flow
- [ ] 4.2 Add `volumeClaimTemplates` to the Kafka `StatefulSet` for `/var/lib/kafka/data`
- [ ] 4.3 Convert Redis and RabbitMQ from `emptyDir` to PersistentVolumeClaims at their data paths
- [ ] 4.4 Declare a requested capacity and `StorageClass` per claim (cluster default in `dev`, explicit in `prod`)
- [ ] 4.5 Write data to each backend, delete/reschedule its pod, and confirm the data persists after the replacement pod re-attaches the claim

## 5. Declarative Deploy Workflow

- [ ] 5.1 Change `.github/workflows/deploy.yml` to `kubectl apply -k k8s/overlays/<env>` (namespace ensured first), removing the raw `kubectl apply -f k8s/` step
- [ ] 5.2 Inject the commit SHA into the image transformer (`kustomize edit set image energyhub-<svc>-service=ghcr.io/<owner>/energyhub-<svc>-service:${GITHUB_SHA}`) and remove the imperative `kubectl set image` step
- [ ] 5.3 Keep the "wait for SHA images in GHCR" gate before applying, and adjust rollout verification/rollback to reference the Kafka `StatefulSet`
- [ ] 5.4 Confirm a deploy runs the SHA-tagged images from the rendered overlay and that `kustomize build` shows the exact SHA before apply

## 6. Validation

- [ ] 6.1 Confirm every stateful backend's rendered manifest is PVC-backed with no `emptyDir` at its data path
- [ ] 6.2 Confirm Kafka runs in KRaft mode as a `StatefulSet` with no Zookeeper resource in the cluster
- [ ] 6.3 Confirm both overlays build and the deploy applies pinned images declaratively (no `kubectl set image`)
- [ ] 6.4 Run `openspec validate k8s-production-robustness --strict` and confirm the change is valid
