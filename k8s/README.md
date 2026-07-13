# ☸️ `k8s/` — Orquestração com Kubernetes (Fase 16)

Árvore declarativa de manifestos que descreve **toda a plataforma EnergyHub** como estado desejado
de um cluster Kubernetes: um `Namespace` `energyhub`, um `Deployment`/`Service` por microsserviço
(auth, client, contract, financial, audit), os componentes de plataforma (Consul, Traefik) e os
backends stateful (PostgreSQL, Redis, RabbitMQ, Kafka + Zookeeper), além de `ConfigMap`s/`Secret`,
`Ingress` e `HorizontalPodAutoscaler`s.

> Consome as **imagens da Fase 14** e as **fronteiras de serviço da Fase 15**. Não há mudança de
> código de aplicação — apenas a camada de orquestração.

---

## 🗺️ O que roda no cluster

| Camada | Recursos | DNS interno |
| :----- | :------- | :---------- |
| **Microsserviços** | `Deployment` + `Service` (ClusterIP) + `HPA` — auth/client/contract/financial/audit | `auth-service:8001` … `audit-service:8005` |
| **Gateway** | `traefik` (`Deployment`) + `traefik-service` (**LoadBalancer**) + `traefik-config` | `traefik-service:80` (web) · `:8080` (dashboard) |
| **Discovery** | `consul` (`Deployment`) + `consul-service` (ClusterIP) | `consul-service:8500` |
| **Borda** | `energyhub-ingress` (`Ingress`, classe `nginx`) → `traefik-service:80` | host `energyhub.local` |
| **Backends stateful** | `postgres` (+ initdb), `redis`, `rabbitmq`, `kafka`, `zookeeper` | `postgres-service:5432`, `redis-service:6379`, `rabbitmq-service:5672`, `kafka-service:9092` |
| **Config** | `energyhub-config` (compartilhado) + `<svc>-config` (por serviço) + `energyhub-secret` | — |

### Fluxo de tráfego

```
cliente → energyhub.local (Ingress/NGINX) → traefik-service (LoadBalancer) → Traefik
        → [consulCatalog lê as tags no Consul] → <svc>-service:<porta> → pod pronto
```

O roteamento por prefixo (`/api/v1/auth`, `/api/v1/clients`, …) e os middlewares de borda
(`eh-ratelimit`, `eh-auth` forwardAuth) vêm das **tags `traefik.*` que cada serviço publica no
Consul** ao se registrar (Fase 15). O provider **Docker do Traefik NÃO é usado** (não alcança o
daemon no Windows) — apenas o `consulCatalog`.

---

## 🔧 Pré-requisitos

- `kubectl` apontando para um cluster local (**minikube** ou **kind**).
- Um **ingress controller** (ex.: NGINX Ingress).
- O **Metrics Server** (para os HPAs).
- As imagens da Fase 14 construídas localmente (`energyhub-<svc>-service:latest`).

### Modelo de configuração — ConfigMap × Secret

- **`ConfigMap`** (não sensível): `ENVIRONMENT`, `CONSUL_HOST/PORT`, `APP_PORT`, `SERVICE_HOST`,
  `REDIS_HOST/PORT`, `KAFKA_BOOTSTRAP_SERVERS`.
- **`Secret`** (sensível): `SECRET_KEY`, `INTERNAL_API_KEY`, senhas e as **`*_DATABASE_URL`/`RABBITMQ_URL`**
  — como a app lê a URL como uma única string que embute a senha, a URL inteira é tratada como
  sensível e fica no Secret (a senha nunca aparece em ConfigMap nem em manifesto de Deployment).
  O `Secret` `energyhub-secret` **não é mais commitado em texto puro**: ele é resolvido **dentro do
  cluster** a partir de um **SealedSecret** cifrado (padrão) ou de um **ExternalSecret** (Vault) —
  ver [`k8s/secrets/`](secrets/README.md). Nunca commitar o `Secret` em claro.

### Backends stateful in-cluster (decisão da Fase 16)

Resolvendo a *Open Question* #3 do design: no cluster **local/dev** os data stores rodam **dentro
do cluster**, endereçados por DNS (`postgres-service`, `redis-service`, …), com `emptyDir`
(efêmero). Em **produção**, troque para managed stores externos ajustando **apenas as URLs no
Secret** — nenhum outro manifesto muda. Para persistir em dev, troque `emptyDir` por `PersistentVolumeClaim`.

---

## 🚀 Subir a plataforma

### 1) Cluster + controladores

```bash
# minikube (driver docker)
minikube start --cpus=4 --memory=6g
minikube addons enable ingress          # NGINX Ingress
minikube addons enable metrics-server   # métricas p/ HPA

# — ou — kind
kind create cluster --name energyhub
# instalar NGINX Ingress + Metrics Server manualmente (ver docs de cada projeto)
```

### 2) Carregar as imagens locais no cluster

As imagens dos serviços são locais (sem registry), por isso os Deployments usam
`imagePullPolicy: IfNotPresent`. Carregue-as no cluster:

```bash
# minikube
for s in auth client contract financial audit; do
  minikube image load energyhub-$s-service:latest
done

# kind
for s in auth client contract financial audit; do
  kind load docker-image energyhub-$s-service:latest --name energyhub
done
```

### 3) Resolver o `energyhub-secret` (sem plaintext no git)

O `Secret` sensível não vive mais em `k8s/secret.yaml`. Antes de aplicar a plataforma, resolva-o
**dentro do cluster** por um dos fluxos de [`k8s/secrets/`](secrets/README.md) — o `kubectl apply -f
k8s/` **não** recorre no subdiretório `secrets/`, então este passo é explícito:

```bash
# Padrão — Sealed Secrets (o controlador expande o SealedSecret cifrado em energyhub-secret):
kubectl apply -f k8s/secrets/energyhub-sealedsecret.yaml

# — ou alternativa — External Secrets Operator (materializa a partir do Vault):
kubectl apply -f k8s/secrets/energyhub-externalsecret.example.yaml

kubectl get secret energyhub-secret -n energyhub   # confirmar que foi criado
```

### 4) Aplicar os manifestos

```bash
kubectl apply -f k8s/namespace.yaml      # namespace primeiro
kubectl apply -f k8s/                     # todo o restante (idempotente; secrets/ resolvido no passo 3)
kubectl get pods -n energyhub -w          # aguardar todos Running/ready
```

### 5) Seed do admin (pós-deploy)

O 1º usuário não pode nascer pela API protegida e as tabelas só existem após cada serviço rodar
`metadata.create_all`. Após o `auth-service` ficar **ready**, insira o admin em `authdb`
(idempotente; mesma hash bcrypt de `ChangeMe123!` da Fase 15):

```bash
kubectl exec -n energyhub deploy/postgres -- \
  psql -U energyhub -d authdb -c "<INSERT do admin/roles — ver docs/ARCHITECTURE.md §20>"
```

---

## ✅ Validação (procedimento da Fase 16)

```bash
# Config e secrets presentes
kubectl get configmap,secret -n energyhub

# Pods prontos + endpoints ligados a pods ready
kubectl get pods -n energyhub
kubectl get endpoints -n energyhub

# Comunicação inter-serviço por DNS do cluster (de dentro de um pod)
kubectl exec -n energyhub deploy/auth-service -- \
  curl -sf http://client-service:8002/health

# Autoscaling — métricas vivas e escala sob carga
kubectl top pods -n energyhub
kubectl get hpa -n energyhub

# Acesso externo pela borda
#   minikube: `minikube tunnel` (LoadBalancer) e/ou mapear energyhub.local no hosts
#   → 127.0.0.1  energyhub.local
curl http://energyhub.local/health

# Fluxo de negócio ponta-a-ponta pelo gateway:
#   login → cria cliente → cria contrato → confere auditoria
```

### Diagnóstico

```bash
kubectl get events -n energyhub --sort-by=.lastTimestamp
kubectl logs -n energyhub deploy/<serviço>
kubectl describe pod -n energyhub <pod>
```

---

## 🧹 Teardown

```bash
kubectl delete namespace energyhub   # remove tudo (blast radius único)
# ou: kubectl delete -f k8s/
```

Remove apenas os manifestos do cluster — não toca no código de aplicação nem em data stores externos.

---

## 🔒 Notas de produção

- **Rotacionar** `SECRET_KEY`, `INTERNAL_API_KEY` e todas as senhas. O `Secret` já **não** é
  commitado em claro — é resolvido no cluster via **SealedSecret** (cifrado) ou **ExternalSecret**
  (Vault); ver [`k8s/secrets/`](secrets/README.md). Nunca commitar o `Secret` em texto puro.
- Trocar os backends `emptyDir` por managed stores externos (URLs no Secret) ou `StatefulSet` + PVC.
- Habilitar **TLS** na borda (cert-manager) e fechar o dashboard do Traefik / UI do Consul.
- Fixar **tags de imagem** explícitas (evitar `latest` em ambientes compartilhados) — Fase 17 (CI/CD).
