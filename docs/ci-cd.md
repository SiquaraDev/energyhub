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
- Um pacote novo nasce **privado**. Para o cluster puxar sem auth, torne-o **público** (Package
  settings → Change visibility) **ou** configure um `imagePullSecret` no cluster.
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
  **`slackapi/slack-github-action@v2`** (`webhook-type: incoming-webhook`).
- **Deploy real:** sem um cluster acessível pelo Actions, `deploy.yml` fica pronto e **pulado** até
  `KUBE_CONFIG` existir; a prova _live_ de deploy roda no `ci-cd.yml` via kind.

---

## 🔒 Segurança

- Nunca comitar credenciais — tudo em **GitHub Secrets**; `GITHUB_TOKEN` tem escopo mínimo por padrão.
- Preferir **tags SHA** (imutáveis) a `:latest` em deploys reprodutíveis (o pin por SHA já faz isso).
- Antes de um deploy real: tornar os pacotes GHCR públicos **ou** configurar `imagePullSecret`, e
  rotacionar as credenciais placeholder herdadas (ver notas das Fases 7/12/15/16).
- Rollback restaura disponibilidade, mas a mudança que falhou **ainda precisa ser investigada** — os
  logs/artefatos e a notificação garantem que a falha não passe silenciosa.

---

<sub>Voltar ao <a href="./README.md">índice da documentação</a> · pipeline: <a href="../.github/workflows/">.github/workflows/</a>.</sub>
