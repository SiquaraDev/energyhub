## Why

Fase 14 containerized the services and Fase 15 split the monolith into deployable microservices, but there is no way to run the whole platform as a coordinated, resilient system: containers are still started by hand or via a single-host Compose file, with no self-healing, no horizontal scaling, and no cluster-managed configuration. This phase declares the platform as Kubernetes manifests so every service runs distributed, is scheduled and restarted automatically, scales under load, and is reachable through a single external entry point.

## What Changes

- Add a `k8s/` manifest tree at the repository root as the single source of truth for the deployed topology: an `energyhub` `Namespace`, and one set of manifests per service (auth, client, contract, financial, audit) plus the platform components (Consul, Traefik/gateway).
- Add a `Deployment` per service with a replica count, the service container image, `resources` requests/limits, and `livenessProbe`/`readinessProbe` on the service `/health` endpoint so unhealthy pods are restarted and traffic only reaches ready pods.
- Add cluster configuration objects: a shared `ConfigMap` and per-service `ConfigMap`s for non-sensitive settings (URLs, ports, environment), and `Secret`s for sensitive values (database password, RabbitMQ password, JWT/`SECRET_KEY`), injected into pods via `env`/`valueFrom` and mounted config volumes.
- Add a `Service` per workload: `ClusterIP` for internal service-to-service calls over stable in-cluster DNS names, and a `LoadBalancer` (Traefik/gateway) as the edge entry point.
- Add an `Ingress` (with an ingress controller) that routes external traffic by host/path to the gateway, plus the local host mapping needed to reach it.
- Add a `HorizontalPodAutoscaler` per service (CPU/memory targets, `minReplicas`/`maxReplicas`) and the Metrics Server dependency so replica counts adjust automatically to load.
- Add a validation procedure that applies all manifests, confirms every pod reaches `Running`/ready, verifies inter-pod communication over cluster DNS, and exercises the end-to-end business flow (login, create client, create contract, audit) through the cluster.

## Capabilities

### New Capabilities

- `service-deployments`: A Kubernetes `Deployment` per microservice defining replicas, container image, resource requests/limits, and liveness/readiness health probes for self-healing scheduling.
- `configuration-and-secrets`: The `energyhub` namespace, `ConfigMap`s for non-sensitive configuration, and `Secret`s for sensitive values, injected into workloads as environment variables and mounted volumes.
- `service-networking`: `Service` objects exposing pods — `ClusterIP` for internal service-to-service DNS and a `LoadBalancer` for the edge — giving each workload a stable in-cluster endpoint.
- `ingress-routing`: An ingress controller and `Ingress` resource routing external HTTP traffic by host/path to the gateway service.
- `horizontal-autoscaling`: `HorizontalPodAutoscaler`s backed by the Metrics Server that scale replicas automatically against CPU and memory utilization targets.
- `cluster-deployment-validation`: An apply-and-verify procedure confirming pod health, inter-service communication over cluster DNS, and the end-to-end business flow across the distributed deployment.

### Modified Capabilities

None — this phase introduces the orchestration layer; no previously specified requirement changes.

## Impact

- **Dependencies**: Requires a Kubernetes cluster (minikube/kind locally), `kubectl`, an ingress controller (e.g. NGINX Ingress), and the Metrics Server for autoscaling. No changes to Python dependencies.
- **Consumes**: The container images built in Fase 14 and the microservice boundaries established in Fase 15; service `/health` endpoints from earlier phases; configuration keys (`DATABASE_URL`, `RABBITMQ_URL`, `SECRET_KEY`, Consul host/port) already used by the services.
- **Provides**: A declarative `k8s/` deployment for the whole platform — namespace, deployments, services, config/secrets, ingress, and autoscalers — that Fase 17 (CI/CD) automates and promotes across environments.
- **New artifacts**: `k8s/namespace.yaml`, `k8s/configmap.yaml`, `k8s/secret.yaml`, per-service `*-deployment.yaml`/`*-service.yaml`/`*-configmap.yaml`/`*-hpa.yaml`, `k8s/ingress.yaml`, and supporting platform manifests (Consul, Traefik).
- **Coordination**: Manifests reference the image tags and container ports produced in Fase 14; in-cluster DNS service names (e.g. `consul-service`, `rabbitmq-service`, `client-service`) replace the Compose hostnames used previously and must match across ConfigMaps and Services.
