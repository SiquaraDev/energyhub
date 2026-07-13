## Context

Fase 14 produced container images for each service and Fase 15 extracted them into independent microservices, but the platform still runs as hand-started containers (or a single Compose file) on one host: there is no self-healing, no horizontal scaling, and no cluster-managed configuration or secrets. This phase declares the runtime topology as Kubernetes manifests so the platform runs distributed, is reconciled to a desired state, and is reachable through one external entry point.

The stack is fixed by the plan: Kubernetes as the orchestrator, targeting a local cluster (minikube/kind) for development, with `kubectl` as the apply tool. The images, container ports, and configuration keys (`DATABASE_URL`, `RABBITMQ_URL`, `SECRET_KEY`, Consul host/port) come from earlier phases and are inputs here, not things this phase changes. Service discovery inside the cluster shifts from Compose hostnames to Kubernetes `Service` DNS names (`consul-service`, `rabbitmq-service`, `client-service`, …), which must be consistent across ConfigMaps, Services, and Deployments.

This is an infrastructure-manifest phase: the deliverable is a declarative `k8s/` tree plus a validation procedure, not application code.

## Goals / Non-Goals

**Goals:**
- Declare a `Deployment` per service with replicas, image, resource requests/limits, and liveness/readiness probes for self-healing scheduling.
- Manage configuration through a namespace, `ConfigMap`s (non-sensitive), and `Secret`s (sensitive), injected into pods via env and volumes.
- Expose services with `ClusterIP` for internal DNS and a `LoadBalancer` at the edge, plus an `Ingress` for host/path routing.
- Provide `HorizontalPodAutoscaler`s and the Metrics Server for automatic CPU/memory-based scaling.
- Validate the deployment: pods ready, inter-pod communication over DNS, and the end-to-end business flow through the cluster.

**Non-Goals:**
- No CI/CD automation or environment promotion — that is Fase 17; manifests are applied manually here.
- No production-grade secret management (Vault/sealed-secrets), TLS/cert issuance, or a service mesh — plaintext `Secret`s and plain HTTP are acceptable for this phase.
- No stateful-workload operators or in-cluster managed databases beyond what the plan sketches; managed data stores remain external configuration.
- No changes to application code, images, or configuration keys — only their orchestration.
- No multi-cluster, multi-region, or GitOps controller (Argo/Flux) setup.

## Decisions

**A per-service manifest set under a single `k8s/` tree, applied as a directory:**
- **Decision:** Author raw YAML manifests grouped per service (`*-deployment.yaml`, `*-service.yaml`, `*-configmap.yaml`, `*-hpa.yaml`) plus shared `namespace.yaml`/`configmap.yaml`/`secret.yaml`/`ingress.yaml`, all applied with `kubectl apply -f k8s/`.
- **Rationale:** Matches the plan's file layout exactly, keeps each service's resources co-located and reviewable, and needs no extra tooling to reason about.
- **Alternative considered:** Helm charts or Kustomize overlays — rejected for this phase; templating adds indirection before there are multiple environments to differentiate. Fase 17 can introduce Kustomize/Helm when environment promotion is needed.

**All resources live in a dedicated `energyhub` namespace:**
- **Decision:** Create one `Namespace` and scope every resource to it.
- **Rationale:** Isolates the platform, gives a single blast radius for `kubectl delete namespace`, and scopes DNS and RBAC cleanly.
- **Alternative considered:** Deploy into `default` — rejected; it mixes platform resources with unrelated workloads and complicates teardown.

**Split configuration into ConfigMaps (non-sensitive) and Secrets (sensitive):**
- **Decision:** Non-sensitive settings (URLs, ports, environment, Consul host/port) go in `ConfigMap`s; passwords and `SECRET_KEY` go in `Secret`s; both are injected via `valueFrom` and, where needed, mounted volumes.
- **Rationale:** Keeps sensitive values out of image layers and `Deployment` manifests, and lets configuration change without rebuilding images.
- **Alternative considered:** Bake configuration into images or put everything in one ConfigMap — rejected; it couples config to image builds and leaks secrets into plaintext manifests.

**ClusterIP for internal traffic, LoadBalancer + Ingress for the edge:**
- **Decision:** Internal services use `ClusterIP` and are addressed by DNS name; the gateway (Traefik) is a `LoadBalancer`, and an `Ingress` (with a controller) provides host/path routing from outside.
- **Rationale:** Internal calls never need external addresses; a single edge (gateway behind ingress) centralizes external exposure and keeps the internal surface private.
- **Alternative considered:** `NodePort` for every service — rejected; it sprawls external ports and bypasses the single-entry-point design from Fase 15.

**Readiness/liveness probes on the existing `/health` endpoint:**
- **Decision:** Both probes call the service `/health` endpoint on the container port, with `initialDelaySeconds`/`periodSeconds` tuned per service startup cost.
- **Rationale:** Reuses the health endpoints already built; readiness gates traffic during startup and liveness recovers wedged pods, giving self-healing for free.
- **Alternative considered:** TCP-socket probes — rejected; a TCP check confirms the port is open but not that the app is actually serving, which `/health` verifies.

**HPA on CPU and memory with explicit min/max bounds:**
- **Decision:** Each scalable service gets a `HorizontalPodAutoscaler` (`autoscaling/v2`) targeting CPU and memory utilization, with `minReplicas`/`maxReplicas`; the Metrics Server supplies utilization data.
- **Rationale:** Matches the plan's targets (e.g. 70% CPU / 80% memory, 2–5 replicas), scales to load, and the explicit bounds cap cost and prevent runaway scaling.
- **Alternative considered:** Fixed replica counts or custom/external metrics (KEDA) — rejected; fixed counts waste resources or under-provision, and custom metrics are premature before there is a queue-depth signal to scale on.

## Risks / Trade-offs

- **In-cluster DNS names must match Compose-era hostnames** → A service that still points at a Compose hostname will fail to resolve. Mitigation: standardize on `*-service` DNS names and keep the same names across ConfigMaps, Services, and env injection; the validation step exercises inter-pod calls by name to catch mismatches.
- **Image tags drift from Fase 14** → `Deployment`s reference image tags that must exist in the registry the cluster can pull from. Mitigation: pin explicit tags (avoid ambiguous `latest` in shared environments) and confirm images are loadable into the local cluster before applying.
- **Plaintext Secrets are only base64-encoded, not encrypted** → Acceptable for a local/dev phase but not for production. Mitigation: document the limitation and defer real secret management (sealed-secrets/Vault) to a later phase; never commit real production credentials.
- **Autoscaling depends on the Metrics Server** → Without it, HPAs report `<unknown>` and never scale. Mitigation: install the Metrics Server as an explicit prerequisite and verify `kubectl get hpa` shows live metrics before relying on scaling.
- **Aggressive liveness probes can cause restart loops** → Too-short `initialDelaySeconds` restarts slow-starting pods before they are ready. Mitigation: set startup delays to cover the service's real boot time and separate readiness (traffic gating) from liveness (restart).
- **LoadBalancer/Ingress behavior differs by environment** → `LoadBalancer` external IPs and ingress addresses work differently on minikube/kind vs. a cloud provider. Mitigation: document the local approach (`minikube tunnel` / ingress addon and `/etc/hosts` host mapping) and keep environment-specific access out of the manifests.
- **Resource requests must fit the local node** → Sum of requests across replicas can exceed a single dev node, leaving pods `Pending`. Mitigation: size requests for the local footprint and scale replica counts down for dev clusters.

## Migration Plan

1. Provision a local cluster (`minikube start` / `kind`) and confirm `kubectl` targets it; create `k8s/namespace.yaml` and apply it.
2. Add shared `configmap.yaml` and `secret.yaml`, then per-service `*-configmap.yaml`; verify keys match what the services expect.
3. Add per-service `*-deployment.yaml` (image, ports, resources, probes, env from ConfigMaps/Secrets) and apply; confirm pods reach `Running`/ready.
4. Add `*-service.yaml` (ClusterIP internal, LoadBalancer for the gateway); verify service-to-service calls resolve by DNS.
5. Install the ingress controller, add `ingress.yaml`, map the platform host locally, and confirm external `/health` access through the gateway.
6. Install the Metrics Server, add `*-hpa.yaml`, and confirm `kubectl get hpa` reports live utilization and scales under load.
7. Apply the full tree (`kubectl apply -f k8s/`), run the end-to-end flow (login → create client → create contract → audit), and inspect `kubectl get pods`/`events`/`logs`.
8. Rollback: this phase adds only cluster manifests; `kubectl delete namespace energyhub` (or `kubectl delete -f k8s/`) removes everything without touching application code or external data stores.

## Open Questions

- Should the local cluster use `LoadBalancer` via `minikube tunnel` or standardize on the ingress addon as the single edge? (Plan shows both a Traefik `LoadBalancer` and an NGINX `Ingress`; reconcile to one edge before Fase 17.)
- Which services are genuinely stateless and safe to autoscale, and which need fixed replicas due to in-memory or connection-bound state? (Deferred; start with stateless services and revisit per service.)
- Do the databases, Redis, and RabbitMQ run in-cluster or remain external managed services referenced by config? (Plan references `*-service` DNS for them; confirm ownership boundary before wiring persistence manifests.)
- What are the per-service resource requests/limits and HPA targets for the target environment? (Plan gives example values; finalize against measured usage from Fase 12 observability.)
