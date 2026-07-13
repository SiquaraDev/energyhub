## Context

The platform's Kubernetes layer was authored in Fase 16 and automated in Fase 17. It works for local validation on minikube/kind, but three decisions taken there were explicitly deferred as "dev-only, harden for production":

- **Images are pinned imperatively.** Each Deployment hard-codes `image: energyhub-<svc>-service:latest` with `imagePullPolicy: IfNotPresent`. The Fase 17 `deploy.yml` then re-pins every service to the immutable SHA tag at deploy time with `kubectl -n energyhub set image deployment/<svc>-service <svc>-service=ghcr.io/<owner>/energyhub-<svc>-service:${GITHUB_SHA}`. The manifests in Git therefore never describe the image that actually runs, and the pin is a side effect of the pipeline rather than a property of the desired state. Fase 17 recorded this as an open question ("should deploy manifests be pinned to the commit-SHA image tag via image substitution instead of `latest`?").
- **Kafka is a single-broker `Deployment` coordinated by a separate Zookeeper `Deployment`.** `kafka.yaml` uses `strategy: Recreate` (so two brokers never race to register `broker.id=1` in Zookeeper), `publishNotReadyAddresses: true` (so the broker can reach its own advertised listener during startup), and a tuned `KAFKA_HEAP_OPTS` to avoid OOMKilled. It has **no volume at all** — the log directory lives on the container's ephemeral writable layer. There is no stable identity and no ordered lifecycle.
- **Every stateful backend uses `emptyDir`.** `postgres.yaml`, `redis.yaml`, and `rabbitmq.yaml` mount `emptyDir: {}` at their data paths; Kafka has no volume. `emptyDir` is tied to the pod's lifetime, so a restart or reschedule discards all data. The Fase 16 README and the `postgres.yaml` header both note "troque `emptyDir` por PVC para persistir".

This change is orchestration-only: it edits `k8s/` manifests and the `deploy.yml` workflow. It introduces no application code and no schema changes. The constraints from earlier phases are fixed: namespace `energyhub`, five services (`auth`/`client`/`contract`/`financial`/`audit`) plus the Traefik gateway, in-cluster stateful backends addressed by DNS (`postgres-service`, `kafka-service`, …), and images published to GHCR as `ghcr.io/<owner>/energyhub-<svc>-service:<sha>`.

## Goals / Non-Goals

**Goals:**
- Manage service image references declaratively through a Kustomize `images:` transformer, pinned to the commit SHA, so the manifest set alone reproduces the running image.
- Structure the manifests as a base plus `dev`/`prod` overlays so environment-specific configuration diverges without forking the base.
- Run Kafka in KRaft mode as a `StatefulSet` with a stable network identity and no Zookeeper dependency.
- Give the stateful backends (at minimum Postgres and Kafka) PVC-backed storage that survives pod restart and rescheduling.
- Make the Fase 17 `deploy.yml` apply the target overlay through Kustomize with the SHA injected, retiring the imperative `kubectl set image` and raw `kubectl apply -f k8s/` steps.

**Non-Goals:**
- No application code, `Dockerfile`, or business-logic changes.
- No move to a real managed cloud store (RDS/MSK) — the stateful backends stay in-cluster; `prod` swaps only the `StorageClass` and (optionally) the connection URLs in the Secret.
- No multi-broker Kafka cluster or replication-factor increase — KRaft here is a single combined broker+controller node, matching the current single-replica topology.
- No GitOps controller (Argo CD/Flux), no Helm, no secret-manager migration (Vault/sealed-secrets) — those remain future work.
- No change to the Ingress, HPA, Consul, or Traefik topologies beyond wiring them into the Kustomize base.

## Decisions

**Kustomize base + overlays, not Helm:**
- **Decision:** Introduce `k8s/base/` (aggregating the current manifests) and `k8s/overlays/{dev,prod}/`, each with a `kustomization.yaml`. Overlays reference the base via `resources: [../../base]` and apply strategic-merge/JSON patches for replicas, resources, ConfigMap values, and storage class.
- **Rationale:** Kustomize is template-free, ships inside `kubectl` (`apply -k`), and layers cleanly over manifests that already exist — no rewrite into a templating language. It keeps the base as the single source of structure and isolates environment drift to small overlay patches.
- **Alternative considered:** Helm — rejected as a heavier packaging model (values templating, releases, Tiller-era muscle memory) that would require re-authoring every manifest as a chart for no benefit at this scale. Raw per-environment manifest copies — rejected as duplication that drifts.

**Declarative SHA pinning via the `images:` transformer:**
- **Decision:** The base declares one `images:` entry per service (`name: energyhub-<svc>-service`, `newName: ghcr.io/<owner>/energyhub-<svc>-service`). The pipeline sets the tag with `kustomize edit set image energyhub-<svc>-service=ghcr.io/<owner>/energyhub-<svc>-service:${GITHUB_SHA}` (or a committed overlay value), and `deploy.yml` applies the built overlay. The Deployment manifests keep a stable placeholder image name that the transformer overrides.
- **Rationale:** The image that runs becomes a property of the rendered manifest, not a post-apply mutation. `kubectl set image` disappears; rollback is a re-apply of a previous render; and any `kustomize build` shows exactly which SHA a deploy will run.
- **Alternative considered:** Keep `kubectl set image` — rejected because it leaves Git describing `:latest` and makes the running image invisible to `kustomize build`/GitOps. Commit the SHA into the manifests each build — rejected as noisy history and a race with the manifest source of truth.

**Kafka in KRaft mode as a `StatefulSet`:**
- **Decision:** Replace the Kafka `Deployment` + Zookeeper `Deployment` with a single-replica Kafka `StatefulSet` in KRaft mode: `KAFKA_PROCESS_ROLES=broker,controller`, a `KAFKA_NODE_ID`, `KAFKA_CONTROLLER_QUORUM_VOTERS` pointing at the pod's stable hostname, `KAFKA_CONTROLLER_LISTENER_NAMES`, and a formatted `CLUSTER_ID`. Front it with a **headless** `Service` for stable DNS identity (`kafka-0.kafka-headless`), keeping the existing `kafka-service` ClusterIP for clients.
- **Rationale:** KRaft removes the whole class of Zookeeper-coupling problems the Fase 16 manifest works around (the `Recreate` strategy exists only to avoid a `broker.id` znode race). A `StatefulSet` gives an ordered, stable identity and a natural home for `volumeClaimTemplates`, which is exactly what a broker's log directory needs.
- **Alternative considered:** Keep Kafka+Zookeeper but add PVCs to both — rejected because it persists the more fragile topology and still needs the `Recreate`/`publishNotReadyAddresses` workarounds. A multi-node KRaft quorum — deferred; overkill for the current single-replica dev/prod-lite scale and a larger resource ask.

**PersistentVolumeClaims for the stateful backends:**
- **Decision:** Replace `emptyDir` with durable storage: Postgres and Kafka get PVCs at their data paths (`/var/lib/postgresql/data`, `/var/lib/kafka/data`), Kafka via a `StatefulSet` `volumeClaimTemplates` and Postgres via a `PersistentVolumeClaim` + `Deployment` (or `StatefulSet`) volume. Redis and RabbitMQ follow the same pattern. The `StorageClass` is left to the cluster default in `dev` (`standard` on minikube/kind) and set explicitly per the target in `prod`.
- **Rationale:** PVCs decouple data lifetime from pod lifetime, so a crash, upgrade, or reschedule no longer wipes the database or the Kafka log. Preserving Postgres's `PGDATA=/var/lib/postgresql/data/pgdata` subdirectory keeps the existing initdb flow intact.
- **Alternative considered:** External managed stores now — deferred (that is the documented `prod` escape hatch of swapping the Secret URLs, out of scope here). `hostPath` volumes — rejected as node-bound and non-portable.

**`deploy.yml` renders the overlay instead of mutating the cluster:**
- **Decision:** Change `deploy.yml` to `kubectl apply -k k8s/overlays/<env>` (namespace first) with the SHA already set in the image transformer, dropping the "wait for images → `set image`" pin step (the SHA-wait remains, since images must exist before apply). Rollout verification and rollback stay.
- **Rationale:** Keeps a single apply that carries the pinned images, so the cluster state matches the rendered overlay and rollback re-applies a known render.
- **Alternative considered:** Leave `deploy.yml` untouched and only add Kustomize files — rejected because the pin would then be applied twice (transformer + `set image`) and the imperative step would still be the effective source of truth.

## Risks / Trade-offs

- **KRaft migration is not in-place for existing data** → A broker that previously ran under Zookeeper cannot simply adopt KRaft on the same log dir. Since dev data is disposable and there is no production Kafka yet, the migration starts from a freshly formatted KRaft volume; document that any pre-existing topic data is not carried over.
- **PVC provisioning depends on a `StorageClass`** → If the target cluster has no default/usable class, PVCs stay `Pending` and pods never start. Mitigation: rely on the minikube/kind default `standard` in `dev` and require an explicit, verified class in the `prod` overlay.
- **`StatefulSet` change alters update semantics** → Ordered, one-at-a-time rollout differs from the Deployment's `Recreate`. For a single replica the behavior is equivalent, but the rollout-status checks in `deploy.yml` must target the `StatefulSet` (and its headless service) rather than a Deployment.
- **Overlay drift** → Base and overlays can fall out of sync (a field patched in `prod` but not `dev`). Mitigation: keep overlays minimal (only genuine per-environment values) and validate every overlay renders with `kustomize build` in CI.
- **Double source of truth during transition** → While both raw `k8s/*.yaml` and `k8s/base/` exist, an operator could `kubectl apply -f k8s/` the old set. Mitigation: move the workload manifests under `base/` and have `deploy.yml` use only `-k`.
- **Deleting a PVC deletes the data** → Durable storage makes teardown less blast-radius-safe than `emptyDir`. Mitigation: document that `kubectl delete namespace energyhub` also removes PVCs, and set a deliberate reclaim policy in `prod`.
- **Cannot fully validate without a live cluster** → As in Fase 16/17, the manifests are authored to the plan and validated by `kustomize build` / `kubeval`-style linting; end-to-end persistence and KRaft behavior are confirmed on minikube/kind and the target cluster.

## Migration Plan

1. Create `k8s/base/kustomization.yaml` listing the existing resources; confirm `kubectl apply -k k8s/base` reproduces today's cluster state.
2. Add the `images:` transformer to the base with a placeholder tag; confirm `kustomize build k8s/base` renders the expected image names.
3. Add `k8s/overlays/dev/` and `k8s/overlays/prod/` referencing the base with their patches; confirm both `kustomize build` cleanly.
4. Replace `kafka.yaml`/`zookeeper.yaml` with a KRaft `StatefulSet` + headless `Service`; deploy to a scratch cluster and confirm the broker becomes ready and accepts topic operations with Zookeeper removed.
5. Convert Postgres and Kafka (then Redis/RabbitMQ) from `emptyDir` to PVCs/`volumeClaimTemplates`; write data, restart the pod, and confirm the data persists.
6. Update `deploy.yml` to `kubectl apply -k k8s/overlays/<env>` with `kustomize edit set image ...:${GITHUB_SHA}`, and remove the `kubectl set image` step; confirm the deployed pods run the SHA-tagged images.
7. Adjust rollout verification/rollback in `deploy.yml` to reference the Kafka `StatefulSet`.
8. Rollback of the change itself: the overlays and StatefulSet are additive/replaceable manifest files; reverting to the prior `k8s/*.yaml` set and the old `deploy.yml` restores the previous behavior (at the cost of durability).

## Open Questions

- Should `prod` keep the stateful backends in-cluster on PVCs, or is this the point to switch Postgres/Kafka to managed services (RDS/MSK) by swapping the Secret URLs — leaving the PVCs as the `dev`-only path?
- Which `StorageClass` and reclaim policy should `prod` require, and should PVCs use `Retain` to survive a namespace delete?
- Should the SHA tag be injected by the pipeline (`kustomize edit set image` at deploy time) or committed into the `prod` overlay per release for a GitOps-style audit trail?
- Should Redis and RabbitMQ also move to `StatefulSet`s for stable identity, or is a `Deployment` + PVC sufficient given they are single-replica?
- Is a single-node KRaft quorum acceptable for `prod`, or should this change already provision a 3-node controller quorum for real fault tolerance?
