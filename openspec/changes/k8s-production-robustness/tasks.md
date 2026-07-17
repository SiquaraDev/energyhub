## 1. Kustomize Base

- [x] 1.1 Create `k8s/base/kustomization.yaml` listing the existing workload resources (namespace, ConfigMaps, Secret, per-service Deployments/Services/HPAs, stateful backends, Consul, Traefik, Ingress)
- [x] 1.2 Move the raw `k8s/*.yaml` workload manifests under `k8s/base/` so the base is the single source of structure
- [x] 1.3 Add an `images:` transformer to the base with one entry per service (`energyhub-<svc>-service` → `newName: ghcr.io/<owner>/energyhub-<svc>-service`) and a stable placeholder tag
- [x] 1.4 Confirm `kustomize build k8s/base` renders the full resource set and every service image resolves from the transformer (no inline `:latest`)

## 2. Environment Overlays

- [x] 2.1 Create `k8s/overlays/dev/kustomization.yaml` referencing the base (`resources: [../../base]`) with dev-only patches (default `StorageClass`, dev replicas/resources, dev ConfigMap values)
- [x] 2.2 Create `k8s/overlays/prod/kustomization.yaml` referencing the base with prod-only patches (explicit `StorageClass`, prod replicas/resources/limits, prod ConfigMap values)
- [x] 2.3 Confirm `kustomize build k8s/overlays/dev` and `kustomize build k8s/overlays/prod` each render cleanly and differ only in the patched environment-specific fields

## 3. Kafka as a KRaft StatefulSet

- [x] 3.1 Author a Kafka `StatefulSet` in KRaft mode (`KAFKA_PROCESS_ROLES=broker,controller`, `KAFKA_NODE_ID`, `KAFKA_CONTROLLER_QUORUM_VOTERS`, `KAFKA_CONTROLLER_LISTENER_NAMES`, formatted `CLUSTER_ID`), dropping `KAFKA_ZOOKEEPER_CONNECT`
- [x] 3.2 Add a headless `Service` (`kafka-headless`) for stable pod identity and keep the `kafka-service` ClusterIP for clients
- [x] 3.3 Remove `k8s/zookeeper.yaml` and the Zookeeper `Deployment`/`Service`, and retire the `Recreate` strategy / `broker.id` znode workaround
- [x] 3.4 Preserve the tuned `KAFKA_HEAP_OPTS`, resource requests/limits, and readiness/liveness probes adapted for KRaft
- [ ] 3.5 Deploy to a scratch cluster and confirm the broker becomes ready and accepts topic operations with Zookeeper removed

## 4. Persistent Storage

- [x] 4.1 Convert PostgreSQL from `emptyDir` to a PersistentVolumeClaim mounted at `/var/lib/postgresql/data`, preserving `PGDATA=/var/lib/postgresql/data/pgdata` and the initdb ConfigMap flow
- [x] 4.2 Add `volumeClaimTemplates` to the Kafka `StatefulSet` for `/var/lib/kafka/data`
- [x] 4.3 Convert Redis and RabbitMQ from `emptyDir` to PersistentVolumeClaims at their data paths
- [x] 4.4 Declare a requested capacity and `StorageClass` per claim (cluster default in `dev`, explicit in `prod`)
- [ ] 4.5 Write data to each backend, delete/reschedule its pod, and confirm the data persists after the replacement pod re-attaches the claim

## 5. Declarative Deploy Workflow

- [x] 5.1 Change `.github/workflows/deploy.yml` to `kubectl apply -k k8s/overlays/<env>` (namespace ensured first), removing the raw `kubectl apply -f k8s/` step
- [x] 5.2 Inject the commit SHA into the image transformer (`kustomize edit set image energyhub-<svc>-service=ghcr.io/<owner>/energyhub-<svc>-service:${GITHUB_SHA}`) and remove the imperative `kubectl set image` step
- [x] 5.3 Keep the "wait for SHA images in GHCR" gate before applying, and adjust rollout verification/rollback to reference the Kafka `StatefulSet`
- [ ] 5.4 Confirm a deploy runs the SHA-tagged images from the rendered overlay and that `kustomize build` shows the exact SHA before apply

## 6. Validation

- [x] 6.1 Confirm every stateful backend's rendered manifest is PVC-backed with no `emptyDir` at its data path
- [x] 6.2 Confirm Kafka runs in KRaft mode as a `StatefulSet` with no Zookeeper resource in the cluster
- [x] 6.3 Confirm both overlays build and the deploy applies pinned images declaratively (no `kubectl set image`)
- [x] 6.4 Run `openspec validate k8s-production-robustness --strict` and confirm the change is valid

---

## Notas de aplicação

**Estado: 22/25 feitas.** As 3 em aberto (3.5, 4.5, 5.4) exigem um **cluster vivo** — nenhuma é
esquecimento; a decisão acordada foi validar offline agora e diferir o live para o CI/cluster.

### Decisões que mudaram a implementação (aprovadas antes de aplicar)

1. **Escopo dos workflows — os DOIS, não só o `deploy.yml`.** As tasks 5.x só nomeiam `deploy.yml`,
   mas mover os manifestos para `k8s/base/` quebra o `ci-cd.yml` (fazia `kubectl apply -f k8s/` no
   kind). Migrei ambos para `apply -k`: `ci-cd.yml` → overlay **dev** (imagens locais que o `kind
   load` carrega), `deploy.yml` → overlay **prod** (ghcr/sha). Sem isso, o pipeline verde quebraria
   no próximo push.
2. **Imagens: dev local, prod ghcr/sha** (não dev também em ghcr). O overlay dev **herda** os nomes
   locais da base; só o prod troca para o registry. Casa com o `kind load` e mantém o CI rápido.
3. **Validação offline** (`kubectl kustomize` + kubeconform), live diferido — daí 3.5/4.5/5.4 abertas.

### Desvio consciente do design.md — semântica do `images:` transformer (approach B)

O design (e o cenário da spec) ilustra a base com `newName: ghcr.io/<owner>`. **Testei com
`kubectl kustomize` e isso NÃO compõe**: se a base reescreve `newName`, o transformer do overlay
keyeado pelo nome ORIGINAL (`energyhub-<svc>-service`) é ignorado — o transformer da base roda
primeiro e renomeia a imagem antes de o overlay ver. Ambos os overrides (dev e prod) viravam no-op
silencioso. Solução adotada: a **base fixa só a TAG** (`newTag: latest`), preservando o NOME
`energyhub-<svc>-service`; assim a base rende o nome LOCAL (dev), e o overlay prod, keyeando pelo
mesmo nome original, sobrepõe `newName=ghcr + newTag=<sha>`. É o que faz o comando da task 5.2
(`kustomize edit set image energyhub-<svc>-service=…`) de fato casar. Todas as SHALL da spec seguem
satisfeitas (uma entrada por serviço; pin por SHA via newName+newTag no prod; base sem tag inline).

### Desvio da task 5.2 — `sed` em vez de `kustomize edit set image`

A task pede `kustomize edit set image`, que exige o **binário `kustomize` standalone** (o `kubectl`
não tem o subcomando `edit`). Adicionar um download não-fixado desse binário ao runner contradiria
o endurecimento de supply-chain da mudança anterior (pins por SHA). Em vez disso, o `deploy.yml` usa
o `kubectl kustomize` **embutido** + um `sed` escopado que injeta o `${GITHUB_SHA}` em cada `newTag:`
do overlay prod (só as 5 entradas de serviço têm `newTag:`; o gateway fica fora do bloco `images:`
do prod, então não é marcado com o SHA). Verificado: o sed rende os 5 serviços em `ghcr.io/…:<sha>`.

### Achados durante a aplicação (corrigidos)

- **NetworkPolicy órfã do Zookeeper**: `allow-zookeeper-ingress` sobrava (zookeeper foi removido).
  Removida. E a policy do Kafka só liberava `:9092`; adicionei `:9093` (porta do controller KRaft —
  o broker fala com o próprio controller no quórum de nó único; sob default-deny num CNI que aplica
  policy a tráfego pod→próprio-IP, sem isso o quórum não forma). Pego pelo kubeconform.
- **Entrada do gateway no transformer**: a spec pede uma entrada `images:` "para cada serviço … e o
  gateway". Adicionei `{name: traefik, newTag: v3.1}` **só na base** (não no bloco prod, senão o
  `sed` do SHA marcaria o traefik com uma tag inexistente).
- **Passo `scale --replicas=1` do CI ficou redundante** e foi removido: o overlay dev já rende
  réplica única.

### Validado offline (antes de qualquer cluster)

| Verificação | Ferramenta | Resultado |
| :-- | :-- | :-- |
| Composição do `images:` transformer base→overlay | `kubectl kustomize` (teste scratch) | approach B correto |
| Build dos overlays dev + prod | `kubectl kustomize` | ambos OK |
| Schema do overlay dev renderizado | `kubectl kustomize \| kubeconform -strict` (k8s 1.34) | **54/54 válidos** |
| Schema do overlay prod renderizado | idem | **54/54 válidos** |
| dev rende imagens LOCAIS + réplicas 1 | inspeção do render | 5 svc `:latest`, 10 Deploy replicas 1 |
| prod rende ghcr + storageClass explícita + HPA 3/10 | inspeção do render | ok |
| Injeção do SHA no prod (o que o deploy.yml faz) | `sed` + `kubectl kustomize` | 5 svc `ghcr.io/…:<sha>` |
| Nenhum `emptyDir` nos backends stateful | grep no render | 0 emptyDir; 3 PVC + 1 volumeClaimTemplate |
| Kafka = StatefulSet KRaft, zero Zookeeper | grep no render | ok |
| Lint dos 2 workflows migrados | `actionlint 1.7.7` | 0 achados |
| `openspec validate --strict` | openspec | (ver 6.4) |

### As 3 tarefas em aberto (live-only)

- **3.5** — broker KRaft ready + operações de tópico com Zookeeper fora. Manifesto validado por
  schema + contrato de env do KRaft (Confluent); a prontidão viva roda no `deploy.yml` (cluster
  real, que agora aguarda `statefulset/kafka`) ou num minikube. O kind do CI aplica o StatefulSet
  mas **não** o aguarda (peso/RAM, como o antigo Kafka/Zookeeper).
- **4.5** — escrever dado, matar o pod, confirmar persistência. Exige provisionamento real de PV.
- **5.4** — a metade "`kustomize build` mostra o SHA exato" está **provada** offline (sed + build);
  a metade "um deploy roda as imagens SHA" precisa do cluster real (`deploy.yml` atrás de `KUBE_CONFIG`).
