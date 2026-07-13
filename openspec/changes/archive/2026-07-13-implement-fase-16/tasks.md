## 1. Cluster and Manifest Scaffolding

- [x] 1.1 Provision a local Kubernetes cluster (`minikube start` or `kind create cluster`) and confirm `kubectl` targets it
- [x] 1.2 Create the `k8s/` directory at the repository root as the manifest source of truth
- [x] 1.3 Create `k8s/namespace.yaml` defining the `energyhub` `Namespace` and apply it

## 2. Configuration and Secrets

- [x] 2.1 Create the shared `k8s/configmap.yaml` (`energyhub-config`) with non-sensitive keys (environment, Consul host/port)
- [x] 2.2 Create per-service `*-configmap.yaml` files carrying each service's config (app name, port, database/redis/rabbitmq URLs)
- [x] 2.3 Create `k8s/secret.yaml` (`energyhub-secret`) with database password, RabbitMQ password, and `SECRET_KEY`
- [x] 2.4 Apply the ConfigMaps and Secrets and verify they exist in the `energyhub` namespace (`kubectl get configmap,secret -n energyhub`)

## 3. Service Deployments

- [x] 3.1 Create `k8s/auth-service-deployment.yaml` with replicas, image, container port, and env from ConfigMap/Secret refs
- [x] 3.2 Add `resources.requests`/`resources.limits` (CPU, memory) to the auth-service deployment
- [x] 3.3 Add `livenessProbe` and `readinessProbe` against `/health` on the auth-service container port, with startup delays
- [x] 3.4 Create deployments for the remaining services (client, contract, financial, audit) following the same pattern
- [x] 3.5 Create platform-component deployments (`consul-deployment.yaml`, `traefik-deployment.yaml`)
- [x] 3.6 Mount the per-service ConfigMap as a config volume where the service reads a config file
- [x] 3.7 Apply the deployments and confirm all pods reach `Running`/ready (`kubectl get pods -n energyhub`)

## 4. Service Networking

- [x] 4.1 Create `k8s/auth-service-service.yaml` (`ClusterIP`) selecting auth-service pods and exposing its port
- [x] 4.2 Create `ClusterIP` services for the remaining internal services (client, contract, financial, audit)
- [x] 4.3 Create `k8s/consul-service.yaml` (`ClusterIP`) for the Consul component
- [x] 4.4 Create `k8s/traefik-service.yaml` as a `LoadBalancer` exposing the gateway ports
- [x] 4.5 Apply the services and verify each has endpoints bound to ready pods (`kubectl get endpoints -n energyhub`)

## 5. Ingress Routing

- [x] 5.1 Install an ingress controller (e.g. NGINX Ingress) into the cluster
- [x] 5.2 Create `k8s/ingress.yaml` routing the platform host by path to the gateway `Service`
- [x] 5.3 Map the platform host to the ingress address locally (`/etc/hosts` or `minikube tunnel`)
- [x] 5.4 Apply the ingress and confirm external access (`curl http://energyhub.local/health`)

## 6. Horizontal Autoscaling

- [x] 6.1 Install the Metrics Server and confirm pod metrics are reported (`kubectl top pods -n energyhub`)
- [x] 6.2 Create `k8s/auth-service-hpa.yaml` (`autoscaling/v2`) targeting the deployment with CPU/memory targets and `min`/`max` replicas
- [x] 6.3 Create HPAs for the remaining scalable services
- [x] 6.4 Apply the HPAs and confirm they report live utilization (`kubectl get hpa -n energyhub`)
- [x] 6.5 Generate load and observe scale-out toward `maxReplicas`, then scale-in toward `minReplicas`

## 7. Cluster Deployment Validation

- [x] 7.1 Apply the full manifest tree (`kubectl apply -f k8s/`) and confirm every pod is `Running`/ready
- [x] 7.2 Verify inter-service communication over cluster DNS from inside a pod (`curl http://client-service:8002/health`)
- [x] 7.3 Exercise the end-to-end business flow through the gateway: login, create client, create contract, verify audit
- [x] 7.4 Inspect `kubectl get events -n energyhub` and pod logs to confirm no scheduling, config, or connectivity errors
- [x] 7.5 Run `openspec validate implement-fase-16` and confirm the change is valid
