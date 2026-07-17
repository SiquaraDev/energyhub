# 🔁 CI/CD — Automação com GitHub Actions (Fase 17)

Pipeline de **integração e entrega contínuas** do EnergyHub. A cada push, o código é **construído,
testado, imageado, publicado e (opcionalmente) deployado**, com **rollback automático** em falha —
fechando o roadmap na versão `1.0.0`.

Consome, sem alterar: o projeto Poetry (Fase 1), a suíte de testes (Fase 13), os `Dockerfile`s por
serviço (Fase 15) e os manifestos `k8s/` (Fase 16).

---

## 🧭 Os workflows

| Arquivo | Gatilho | O que faz | Estágio |
| :------ | :------ | :-------- | :-----: |
| **[build.yml](../.github/workflows/build.yml)** | push `main`/`master`/`develop`, PR `main`/`master` | `poetry build` + `pytest` (cobertura) + upload ao Codecov | CI |
| **[test.yml](../.github/workflows/test.yml)** | push `main`/`master`/`develop`/`feature/*`, PR `main`/`master`/`develop` | Postgres + Redis (service containers) → passos **unit** e **integração** + artefato | CI |
| **[docker.yml](../.github/workflows/docker.yml)** | push `main`/`master`/`develop`, PR `main`/`master` | matrix Buildx → 1 imagem por serviço → **push no GHCR** (`latest` + SHA) | CI |
| **[deploy.yml](../.github/workflows/deploy.yml)** | push `main`/`master` | `kubectl apply -f k8s/` num cluster **REAL** (`KUBE_CONFIG`) + rollout + **rollback** + Slack | CD |
| **[ci-cd.yml](../.github/workflows/ci-cd.yml)** | push `main`/`master` | esteira encadeada `build-and-test → build-and-push → deploy` (deploy em **kind efêmero**) | CI+CD |

> **Nota de branch.** Este repo usa `master` como default; os gatilhos incluem `main` e `master`
> (e `develop`) para portabilidade. O deploy dispara em `main`/`master`.

---

## 🔐 Secrets necessários

| Secret | Usado por | Obrigatório? |
| :----- | :-------- | :----------- |
| `GITHUB_TOKEN` (automático) | docker.yml, ci-cd.yml | ✅ nativo — publica no GHCR do próprio owner |
| `KUBE_CONFIG` | deploy.yml | ⛔ opcional — **sem ele o deploy é pulado** (verde), não falha |
| `CODECOV_TOKEN` | build.yml | ⛔ opcional — sem ele o upload não derruba o build (`fail_ci_if_error: false`) |
| `SLACK_WEBHOOK_URL` | deploy.yml | ⛔ opcional — notificação de falha só dispara se presente |

Só o `GITHUB_TOKEN` (fornecido pelo Actions) é obrigatório. Os demais habilitam recursos extras e o
pipeline **não quebra** na ausência deles — o repo funciona _out of the box_.

---

## 📦 Registry — GHCR (grátis) e alternativas

As 5 imagens vão para o **GitHub Container Registry**: `ghcr.io/<owner>/energyhub-<serviço>`, com
tags **`:latest`** (rolling) e **`:${{ github.sha }}`** (imutável, rastreável ao commit exato).

- **Login** com `github.actor` + `GITHUB_TOKEN` (sem PAT). Exige `permissions: { packages: write }`.
- O owner do ref OCI é **minúsculo** (`SiquaraDev` → `siquaradev`) — feito via `${GITHUB_REPOSITORY_OWNER,,}`.
- Um pacote novo nasce **privado** — e continua assim. O cluster autentica com o
  **`ghcr-pull-secret`** entregue pelo SA `energyhub-sa` (ver [🔐 Supply chain](#-supply-chain-endurecimento-pós-10)).
- Cada imagem publicada carrega **provenance** (de qual commit/workflow/builder saiu) e **SBOM**
  (inventário de componentes), via `provenance: true`/`sbom: true` no `docker/build-push-action`.
- **Trocar por Docker Hub / AWS ECR:** muda-se apenas o **passo de login** e o **prefixo das tags**
  (secrets `DOCKER_USERNAME`/`DOCKER_PASSWORD`, ou `ECR_REGISTRY` + credenciais AWS / OIDC). A
  estrutura de build/tag/push permanece idêntica.

**Cache de camadas:** GitHub Actions cache (`type=gha,mode=max`, escopo por serviço). Alternativa
_registry-backed_: `cache-from/to: type=registry,ref=ghcr.io/<owner>/energyhub-<svc>:buildcache`.

---

## 🚀 Deploy & rollback

### deploy.yml — cluster real (atrás de `KUBE_CONFIG`)

1. **Gate:** um job lê `KUBE_CONFIG` (via env — secrets não podem ir em `if:`) e emite `has_kubeconfig`.
   Sem o secret, o job `deploy` é **pulado limpo**.
2. **`kubectl` do secret** (`azure/k8s-set-context@v4`, method `kubeconfig`).
3. **Preflight do `energyhub-secret`:** ele **não é versionado** (`harden-security-credentials`); num
   cluster real vem do **SealedSecret/ExternalSecret** ([`k8s/secrets/`](../k8s/secrets/README.md)),
   aplicado **fora** desta esteira. O preflight falha na hora com erro explícito se ele faltar.
4. **`kubectl apply -f k8s/`** — reconcilia o estado desejado. A varredura é **não-recursiva** de
   propósito: `k8s/cert-manager/` e `k8s/secrets/` ficam de fora porque declaram **CRDs** que exigem
   controllers instalados (cert-manager / sealed-secrets) — senão o apply quebra com
   `no matches for kind "Issuer"` em qualquer cluster sem eles.
5. **Pin por SHA:** `kubectl set image deployment/<svc>-service <svc>-service=ghcr.io/<owner>/energyhub-<svc>-service:<sha>`
   fixa a imagem exata do commit **sem editar os manifestos** (resolve a _Open Question_ de rastreabilidade).
6. **Gate de rollout:** `kubectl rollout status` (5 serviços + `traefik`) e `kubectl wait --for=condition=available`.
7. **Rollback (`if: failure()`):** `kubectl rollout undo` reverte para a última revisão boa.
8. **Slack (`if: failure()`):** notifica só se `SLACK_WEBHOOK_URL` existir.

### ci-cd.yml — validação de deploy GRÁTIS (kind efêmero)

O estágio `deploy` do pipeline combinado **não precisa de nenhum cluster 24/7**: sobe um **kind**
no runner, carrega as imagens recém-publicadas (tag SHA → `energyhub-<svc>-service:latest`), cria o
namespace e um **`energyhub-secret` efêmero com credenciais aleatórias** (`openssl rand`) — já que o
Secret deixou de ser versionado e um kind descartável não justifica um controller de selagem; nada
sensível entra no repositório e os valores aleatórios ainda satisfazem a **guarda de produção**
(o ConfigMap usa `ENVIRONMENT=production`). Em seguida roda um
**dry-run server-side de todos os manifestos**, aplica `k8s/`, reduz réplicas para 1 (RAM do runner),
aguarda o **subconjunto core** (Postgres/Redis/RabbitMQ/Consul + auth/client) e executa um **drill de
rollback**: injeta uma imagem quebrada, confirma que o rollout falha e que `rollout undo` recupera.

> **Por que um subconjunto?** Um runner hospedado tem 8–16 GB de RAM; a stack completa (~17 pods,
> incluindo Kafka/Zookeeper) não cabe com folga. O drill prova o **mecanismo** de apply/rollout/rollback;
> a stack completa já foi validada _live_ em minikube na Fase 16.

---

## ⚠️ Reconciliações spec → realidade

O plano da Fase 17 foi escrito antes de as Fases 15/16 materializarem; alguns pontos foram adaptados:

- **Registry:** o plano cita Docker Hub/ECR; adotou-se **GHCR** (grátis, sem secret externo) como
  primário, com Docker Hub/ECR documentados como alternativa por configuração.
- **`api-gateway` na matrix:** não existe imagem `api-gateway` — o gateway é **Traefik** (imagem
  oficial, não construída). A matrix cobre os **5 serviços** com `Dockerfile`; o rollout usa os nomes
  reais de deployment (`auth-service`, `client-service`, `traefik`).
- **`tests/unit` e `tests/integration`:** o repo não usa esses diretórios nem o marcador
  `@pytest.mark.integration`; a integração é **skip-guarded** (pula sem Postgres). Os dois passos
  distintos são obtidos pela presença/ausência do banco (endpoint morto no passo unit).
- **Slack:** `8398a7/action-slack` foi **arquivado (2025)**; usa-se o oficial
  **`slackapi/slack-github-action`** (`webhook-type: incoming-webhook`), hoje pinado em `v4.0.0`.
- **Deploy real:** sem um cluster acessível pelo Actions, `deploy.yml` fica pronto e **pulado** até
  `KUBE_CONFIG` existir; a prova _live_ de deploy roda no `ci-cd.yml` via kind.

---

## 🔐 Supply chain — endurecimento pós-`1.0.0`

A Fase 17 entregou uma esteira que **funciona**; esta camada a torna **confiável**. Três buracos
foram fechados (change `harden-cicd-supply-chain`):

### 1. Pins imutáveis por SHA + Dependabot

Toda action era referenciada por **tag móvel** (`@v7`, `@v1`). Uma tag pode ser reapontada por um
upstream comprometido para executar código arbitrário **com o token do workflow** — o vetor do
incidente `tj-actions`. Agora as **29 referências** (13 actions distintas) usam SHA de 40 chars:

```yaml
uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0
```

O SHA é imutável; o comentário preserva a legibilidade. O
[`.github/dependabot.yml`](../.github/dependabot.yml) abre um PR **agrupado semanal** bumpando SHA e
comentário juntos — sem ele, "pinar" viraria "congelar".

> **O congelamento não era hipotético.** Ao pinar, a auditoria achou **5 das 13 actions presas em
> runtime Node 20** (já depreciado; o runner as forçava para o Node 24 e avisava), todas com major
> nova disponível: `actions/cache` v4→**v6**, `actions/upload-artifact` v4→**v7**,
> `docker/metadata-action` v5→**v6**, `Azure/k8s-set-context` v4→**v5**,
> `slackapi/slack-github-action` v2→**v4** (+ `codecov-action` v5→**v7**). Todas foram subidas junto
> com o pin, após conferir na API que cada input em uso sobreviveu ao bump. Hoje: **zero Node 20**.

### 2. Branch protection (ação de admin — **não aplicada** automaticamente)

Vive nas *settings* do GitHub, fora do YAML — então virou script versionado:
[`.github/branch-protection.sh`](../.github/branch-protection.sh).

```bash
bash .github/branch-protection.sh          # dry-run: mostra o plano, não altera nada
bash .github/branch-protection.sh --apply  # aplica (pede confirmação; precisa ser admin)
bash .github/branch-protection.sh --show   # inspeciona o estado vigente
bash .github/branch-protection.sh --remove --yes   # rollback
```

Regras: push direto bloqueado, ≥1 aprovação, required checks **`build`** + **`test`**, sem
force-push/deleção.

- **Só `build` e `test`** são exigidos: `deploy` está de fora porque **dois** workflows expõem um
  check com esse mesmo nome (ambíguo), e gatear merge em deploy prenderia o PR à disponibilidade do
  registry/cluster. Os checks são fixados ao **app 15368** (GitHub Actions) para que nenhuma outra
  integração satisfaça a exigência publicando um check homônimo.
- **Armadilha do repo solo:** o GitHub **não deixa você aprovar seu próprio PR**. Exigir 1 aprovação
  com `ENFORCE_ADMINS=true` num repo de um mantenedor só **trava todo merge**. Por isso o default é
  `ENFORCE_ADMINS=false` — colaboradores passam pelo fluxo completo e o admin mantém a válvula de
  escape. Só ligue quando houver um segundo mantenedor que possa aprovar.
- Hoje só existe o branch `master`; o script **pula** `main` com aviso em vez de estourar 404.

### 3. Pull autenticado das imagens privadas

Os pacotes GHCR são privados (`GET` anônimo no manifest → `401`). O `kind` do CI **mascarava** isso:
ele pré-carrega as imagens com `kind load` sob outro nome e `imagePullPolicy: IfNotPresent`, então o
kubelet nunca fala com o GHCR — o deploy ficaria verde mesmo com o pull secret quebrado. Duas peças
resolvem, e um probe dedicado impede o falso-positivo:

- [`k8s/serviceaccount.yaml`](../k8s/serviceaccount.yaml) — SA `energyhub-sa` referenciando o
  `ghcr-pull-secret`; os 5 Deployments apontam para ele (um ponto de verdade, não 5 cópias).
- [`k8s/secrets/create-ghcr-pull-secret.sh`](../k8s/secrets/README.md) — cria o Secret a partir de um
  PAT `read:packages` (nunca versionado). No CI, do `GITHUB_TOKEN` **efêmero** do run.
- **`Verify GHCR pull secret pulls a PRIVATE image`** (em `ci-cd.yml`) — sobe um pod que referencia a
  imagem pelo nome **remoto** com `imagePullPolicy: Always`, forçando um pull autenticado real.
- O `deploy.yml` ganhou um **preflight** do `ghcr-pull-secret`, simétrico ao do `energyhub-secret`.

A alternativa (**pacotes públicos**, dispensando o secret) está documentada com o trade-off em
[`k8s/secrets/README.md`](../k8s/secrets/README.md#-alternativa-tornar-os-pacotes-públicos).

### 4. Concurrency + least-privilege

Todo workflow declara `concurrency: { group: <workflow>-<ref>, cancel-in-progress: true }` — um push
novo cancela o run em voo. Crítico no `deploy.yml`/`ci-cd.yml`: sem o guard, dois commits em
sequência disputam o cluster e **o rollout do commit mais antigo pode vencer**. O default de
`permissions` segue `contents: read`, com `packages: write` só no job que publica e `packages: read`
no que só puxa.

---

## 🔒 Segurança

- Nunca comitar credenciais — tudo em **GitHub Secrets**; `GITHUB_TOKEN` tem escopo mínimo por padrão.
- Preferir **tags SHA** (imutáveis) a `:latest` em deploys reprodutíveis (o pin por SHA já faz isso).
- Antes de um deploy real: provisionar o **`ghcr-pull-secret`** (`k8s/secrets/create-ghcr-pull-secret.sh`)
  — os preflights do `deploy.yml` falham cedo e com mensagem explícita se ele ou o `energyhub-secret`
  faltarem. Rotacionar as credenciais placeholder herdadas (ver notas das Fases 7/12/15/16).
- **Aplicar a branch protection** (`bash .github/branch-protection.sh --apply`) — é uma ação de
  **admin**, deliberadamente fora de qualquer esteira automática.
- Rollback restaura disponibilidade, mas a mudança que falhou **ainda precisa ser investigada** — os
  logs/artefatos e a notificação garantem que a falha não passe silenciosa.

---

<sub>Voltar ao <a href="./README.md">índice da documentação</a> · pipeline: <a href="../.github/workflows/">.github/workflows/</a>.</sub>
