# ☸️ `k8s/` — Orquestração com Kubernetes (Fase 16)

Árvore declarativa de manifestos que descreve **toda a plataforma EnergyHub** como estado desejado
de um cluster Kubernetes: um `Namespace` `energyhub`, um `Deployment`/`Service` por microsserviço
(auth, client, contract, financial, audit), os componentes de plataforma (Consul, Traefik) e os
backends stateful (PostgreSQL, Redis, RabbitMQ e **Kafka em modo KRaft**), além de `ConfigMap`s/`Secret`,
`Ingress` e `HorizontalPodAutoscaler`s.

> Consome as **imagens da Fase 14** e as **fronteiras de serviço da Fase 15**. Não há mudança de
> código de aplicação — apenas a camada de orquestração.

> **📦 Estrutura Kustomize (k8s-production-robustness).** Os manifestos de workload vivem sob
> [`k8s/base/`](base/) e são aplicados por **overlays**: [`k8s/overlays/dev/`](overlays/dev/)
> (imagens locais, réplica única, StorageClass default) e [`k8s/overlays/prod/`](overlays/prod/)
> (imagens `ghcr.io/<owner>/…@<sha>`, StorageClass explícita, HPAs maiores). Aplica-se com
> `kubectl apply -k k8s/overlays/<env>` — **não** mais `kubectl apply -f k8s/`. Fora da base, porque
> dependem de controllers/segredos aplicados à parte: [`cert-manager/`](cert-manager/) e
> [`secrets/`](secrets/).

---

## 🗺️ O que roda no cluster

| Camada | Recursos | DNS interno |
| :----- | :------- | :---------- |
| **Microsserviços** | `Deployment` + `Service` (ClusterIP) + `HPA` — auth/client/contract/financial/audit | `auth-service:8001` … `audit-service:8005` |
| **Gateway** | `traefik` (`Deployment`) + `traefik-service` (**LoadBalancer**) + `traefik-config` | `traefik-service:80` (web) · `:8080` (dashboard) |
| **Discovery** | `consul` (`Deployment`) + `consul-service` (ClusterIP) | `consul-service:8500` |
| **Borda** | `energyhub-ingress` (`Ingress`, classe `nginx`) → `traefik-service:80` | host `energyhub.local` |
| **Backends stateful** | `postgres` (+ initdb), `redis`, `rabbitmq` — todos **PVC-backed**; `kafka` = **StatefulSet KRaft** (+ `kafka-headless`) | `postgres-service:5432`, `redis-service:6379`, `rabbitmq-service:5672`, `kafka-service:9092` |
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

### Backends stateful in-cluster (Fase 16 + k8s-production-robustness)

No cluster **local/dev** os data stores rodam **dentro do cluster**, endereçados por DNS
(`postgres-service`, `redis-service`, …). Desde o endurecimento, o armazenamento é **durável**: cada
backend monta um **`PersistentVolumeClaim`** (Postgres/Redis/RabbitMQ) ou um `volumeClaimTemplate`
(Kafka), não mais `emptyDir` — o dado **sobrevive a restart/reschedule** do pod. O `StorageClass`
fica implícito (default do cluster) em `dev` e **explícito** no overlay `prod`. Em **produção**,
alternativamente, troque para managed stores externos ajustando **apenas as URLs no Secret**.

O **Kafka** roda em **modo KRaft** como `StatefulSet` (sem Zookeeper), com identidade estável via o
Service headless `kafka-headless` e log persistente no PVC. Os clientes seguem usando
`kafka-service:9092`, inalterado.

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

### 2) Construir e carregar as imagens locais no cluster

As imagens dos serviços são locais (sem registry), por isso os Deployments usam
`imagePullPolicy: IfNotPresent`. Primeiro **construa-as** (elas nascem do `docker compose` da Fase 14 —
nomes `energyhub-<svc>-service:latest`):

```bash
docker compose build auth-service client-service contract-service financial-service audit-service
```

Depois carregue-as no cluster:

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
**dentro do cluster** por um dos fluxos de [`k8s/secrets/`](secrets/README.md) — `secrets/` fica
**fora da base Kustomize** (o `apply -k` não o inclui), então este passo é explícito:

```bash
# Namespace primeiro — o Secret é namespaced (energyhub); aplicá-lo antes falha com "namespace not found":
kubectl apply -f k8s/base/namespace.yaml

# Padrão — Sealed Secrets. Atenção: energyhub-sealedsecret.yaml NÃO existe num clone novo — é a saída
# do kubeseal. Antes deste apply: instale o controlador (secrets/sealed-secrets-controller.md),
# preencha o *.local.yaml e rode `bash k8s/secrets/seal-secrets.sh` (passo a passo em secrets/README.md §A):
bash k8s/secrets/seal-secrets.sh                              # gera k8s/secrets/energyhub-sealedsecret.yaml
kubectl apply -f k8s/secrets/energyhub-sealedsecret.yaml     # o controlador o expande em energyhub-secret

# — ou alternativa — External Secrets Operator (materializa a partir do Vault; precisa do ESO + Vault):
# kubectl apply -f k8s/secrets/energyhub-externalsecret.example.yaml

kubectl get secret energyhub-secret -n energyhub   # confirmar que foi criado
```

### 4) Aplicar os manifestos (via Kustomize)

```bash
# (o namespace já foi criado no passo 3, antes do Secret; este apply é idempotente)
kubectl apply -k k8s/overlays/dev         # renderiza a base + patches de dev e aplica (idempotente)
kubectl get pods -n energyhub -w          # aguardar todos Running/ready

# Inspecionar o que SERÁ aplicado, sem aplicar (o build mostra imagens, PVCs, StatefulSet):
kubectl kustomize k8s/overlays/dev
```

> Em **produção** use o overlay `prod` (`kubectl apply -k k8s/overlays/prod`) — ele fixa as imagens
> em `ghcr.io/<owner>/…` e exige uma `StorageClass` explícita (ajuste o placeholder `gp3` em
> [`overlays/prod/kustomization.yaml`](overlays/prod/kustomization.yaml) ao seu cluster). A esteira
> `deploy.yml` injeta o commit SHA nas imagens do `prod` antes do apply.

### 5) Seed do admin (pós-deploy)

O 1º usuário não pode nascer pela API protegida, e as tabelas só existem após o `auth-service` rodar
`metadata.create_all`. O seed completo (3 papéis, catálogo de permissões e o vínculo do admin) é
definido pelas **migrações Alembic do monólito `0008`–`0011`**
([`../energyhub/alembic/versions/`](../energyhub/alembic/versions/)) — a **fonte da verdade** do schema de
`auth`. Por política de segurança **nenhum hash de senha é commitado**, então não há INSERT pronto aqui.

Ainda **não há um `Job` de seed** no `k8s/base/` (pendência conhecida) — o passo é manual. Gere o hash a
partir da **sua** `ADMIN_PASSWORD` e aplique o seed em `authdb` após o `auth-service` ficar **ready**:

```bash
# 1) hash bcrypt (custo 12) a partir da SUA senha — nunca commitar:
HASH=$(ADMIN_PASSWORD='<sua-senha-admin>' python -c \
  "import bcrypt,os;print(bcrypt.hashpw(os.environ['ADMIN_PASSWORD'].encode()[:72],bcrypt.gensalt(12)).decode())")

# 2) insira o admin com o $HASH (ajuste ao schema de auth). O vínculo ao papel ADMIN e o catálogo de
#    permissões vêm das migrações 0008/0009 — a forma robusta é rodar essas migrações contra authdb:
kubectl exec -n energyhub -i deploy/postgres -- psql -U energyhub -d authdb <<SQL
INSERT INTO users (id, username, password, email, full_name, active)
VALUES (gen_random_uuid(), 'admin', '$HASH', 'admin@energyhub.local', 'Administrador', true)
ON CONFLICT (username) DO UPDATE SET password = EXCLUDED.password;
SQL
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
kubectl delete namespace energyhub   # remove tudo (blast radius único; apaga também os PVCs)
# ou: kubectl delete -k k8s/overlays/dev   # (o overlay aplicado; NÃO remove os PVCs por si só)
```

Remove os manifestos do cluster — não toca no código de aplicação nem em data stores externos.
**Atenção:** com PVCs, `delete namespace` **apaga os volumes** (e os dados). O `delete -k` não remove
os PVCs criados por `volumeClaimTemplates`; limpe-os à parte se quiser um teardown completo.

---

## 🔒 Notas de produção

- **Rotacionar** `SECRET_KEY`, `INTERNAL_API_KEY` e todas as senhas. O `Secret` já **não** é
  commitado em claro — é resolvido no cluster via **SealedSecret** (cifrado) ou **ExternalSecret**
  (Vault); ver [`k8s/secrets/`](secrets/README.md). Nunca commitar o `Secret` em texto puro.
- Os backends já são **PVC-backed** (Postgres/Redis/RabbitMQ + Kafka em `volumeClaimTemplate`) — o
  dado sobrevive a restart/reschedule. Em produção, alternativamente troque para managed stores
  externos ajustando só as URLs no `Secret`, e defina uma `StorageClass` explícita no overlay `prod`.
- **TLS de borda já habilitado** via cert-manager + Ingress (Secret `energyhub-tls`, `force-ssl-redirect`);
  o **dashboard do Traefik está fechado** (`api.insecure: false` + basic-auth no entrypoint interno) e a
  **UI do Consul removida** (sem `-ui`). Em produção real, troque a CA interna auto-assinada por um issuer
  confiável (Let's Encrypt / CA corporativa).
- Fixar **tags de imagem** explícitas (evitar `latest` em ambientes compartilhados) — Fase 17 (CI/CD).
