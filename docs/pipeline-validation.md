# ✅ Registro de validação da esteira — EnergyHub `1.0.0`

> **Atestação datada e pontual.** Este documento registra que a esteira de CI/CD da Fase 17 foi
> **provada verde de ponta a ponta nos runners hospedados do GitHub**, para os commits citados
> abaixo. É a prova durável do marco "entregue continuamente" — os logs e o histórico do GitHub
> Actions **expiram**, mas este registro (e os fatos imutáveis que ele cita: SHAs, tags de imagem,
> correções aplicadas) permanece auditável no repositório.
>
> **Data:** 2026-07-17 · **Commit validado (canônico):** `434a094` · **Owner GHCR:** `siquaradev`

Origem: change OpenSpec **`validate-pipeline-live`** (reduzida). As três capacidades de execução
(`live-pipeline-execution`, `ghcr-publication-verification`, `ephemeral-deploy-drill-validation`)
foram provadas **ao vivo** como efeito dos pushes das mudanças pós-`1.0.0` — este registro as
consolida em `pipeline-validation-record`.

---

## 1. Os 5 workflows verdes nos runners hospedados

Para o push do commit **`434a094`** ("feat(k8s)!: migra deploy para Kustomize (base/overlays) + Kafka
KRaft sem Zookeeper"), em `ubuntu-latest`:

| Workflow | Conclusão | Run |
| :------- | :-------- | :-- |
| **Build** | ✅ success | [actions/runs/29618122084](https://github.com/SiquaraDev/energyhub/actions/runs/29618122084) |
| **Test** | ✅ success | [actions/runs/29618122100](https://github.com/SiquaraDev/energyhub/actions/runs/29618122100) |
| **Docker** | ✅ success | [actions/runs/29618122109](https://github.com/SiquaraDev/energyhub/actions/runs/29618122109) |
| **CI/CD Pipeline** | ✅ success | [actions/runs/29618122035](https://github.com/SiquaraDev/energyhub/actions/runs/29618122035) |
| **Deploy** | ✅ success (gate pulado) | [actions/runs/29618122064](https://github.com/SiquaraDev/energyhub/actions/runs/29618122064) |

> A esteira permaneceu verde ao longo da **série** de pushes pós-`1.0.0` — `302ca5e`, `ae27d4e`,
> `6bf0181`, `434a094` — não apenas num commit isolado.

---

## 2. Publicação no GHCR (`latest` + SHA + attestations)

As 5 imagens de serviço publicadas em `ghcr.io/siquaradev/energyhub-<serviço>-service`, confirmado por
consulta direta ao registry (HTTP 200) para `434a094`:

| Serviço | `:latest` | `:434a094…` (SHA) |
| :------ | :-------: | :----------------: |
| `energyhub-auth-service` | ✅ 200 | ✅ 200 |
| `energyhub-client-service` | — | ✅ 200 |
| `energyhub-contract-service` | — | ✅ 200 |
| `energyhub-financial-service` | — | ✅ 200 |
| `energyhub-audit-service` | — | ✅ 200 |

*(A tag `:latest` foi verificada no `auth-service`; o `docker.yml`/`ci-cd.yml` publica `latest` + SHA
para os 5 na mesma matriz.)*

**Provenance + SBOM:** desde `harden-cicd-supply-chain`, o build usa `provenance: true`/`sbom: true`.
O índice OCI carrega, além da imagem `linux/amd64`, um manifesto `attestation-manifest` — **confirmado
concretamente** na inspeção do índice em `ae27d4e`. A mesma configuração de build se aplica a todo
push subsequente (`434a094` incluído).

---

## 3. Deploy efêmero (kind) + drill de rollback

O job `deploy` do `ci-cd.yml` rodou de verdade num **kind** no runner (run
[29618122035](https://github.com/SiquaraDev/energyhub/actions/runs/29618122035)), com todos os passos
verdes:

```
[success] Apply dev overlay              ← kubectl apply -k k8s/overlays/dev (Kustomize)
[success] Wait for core stack to be ready
[success] Verify GHCR pull secret pulls a PRIVATE image
[success] Rollback drill (injected failure)
```

Evidência de que os backends **PVC-backed** subiram e o drill recuperou (trecho do log):

```
persistentvolumeclaim/postgres-data created
statefulset.apps/kafka created
deployment.apps/postgres condition met        ← postgres SOBRE PVC ficou Available (PVC deu bind)
...
rollout falhou como esperado — revertendo...  ← imagem quebrada injetada → rollout não conclui
rollback recuperou o auth-service ✅          ← rollout undo → recuperação
```

O `postgres condition met` é a prova de que o `PersistentVolumeClaim` **fez bind** num volume real do
kind. O KRaft do Kafka **não** é aguardado no CI (peso/RAM do runner) — sua prontidão viva é validada
no `deploy.yml` (cluster real) / minikube.

---

## 4. Catálogo de correções _fix-forward_ (achadas ao vivo)

O valor de rodar de verdade: cada uma destas só apareceu fora do ambiente local. Registradas com
**como foram achadas** — porque nem todas quebraram um run (algumas foram pegas por inspeção de log ou
revisão adversarial de um run **verde**).

| # | Sintoma | Como foi achada | Causa | Correção | Commit |
| :- | :------ | :-------------- | :---- | :------- | :----- |
| 1 | `no matches for kind "Issuer"` | **run VERMELHO** (CI/CD Pipeline) | `apply -f k8s/` não-recursivo puxava os CRDs do cert-manager | mover o issuer para `k8s/cert-manager/` (fora da varredura) | `302ca5e` |
| 2 | Docker falhando | **run VERMELHO** (Docker) | **incidente do GitHub** (página 500 "Unicorn"), não bug nosso | re-run **sem tocar em código** → verde (prova de que era externo) | — |
| 3 | `sleep: missing operand` | inspeção de log de um run **VERDE** | crase num comentário dentro de heredoc **não-quotado** → o bash executou o texto | mover a explicação para fora do heredoc + aviso | `6bf0181` |
| 4 | `--show` diz "sem proteção" | verificação manual (script) | `\| jq` externo ausente no Git Bash; `\|\| echo` engoliu o erro | usar o `--jq` embutido do `gh` + distinguir 404 de erro | `6bf0181` |
| 5 | Kafka crashloop no boot | **revisão adversarial ANTES do push** | `CLUSTER_ID` inválido (21 chars; não decodifica p/ 16 bytes) → `kafka-storage format` rejeita | UUID base64url de 16 bytes válido | pré-`434a094` |

> Nenhuma correção **afrouxou** um critério de aceite — cada uma produziu um run genuinamente verde.
> Um padrão se repetiu (#2, #3, #4): **ler falha de comando/incidente como resposta** — foi o gatilho
> de vários dos erros e das correções.

---

## 5. Postura de secrets — a esteira é verde _out-of-the-box_

A esteira roda verde com **apenas o `GITHUB_TOKEN`** ambiente. Os demais secrets são **opcionais** e a
degradação sem eles é o comportamento **intencional** (padrão de gate/soft-fail/no-op da Fase 17):

| Secret | Ausente → efeito | Como habilitar |
| :----- | :--------------- | :------------- |
| `CODECOV_TOKEN` | upload de cobertura **soft-fail** (`fail_ci_if_error: false`) — não derruba o `Build` | *Settings → Secrets → Actions*; token do Codecov |
| `KUBE_CONFIG` | o job-gate emite `has_kubeconfig=false` e o `deploy` (cluster real) é **pulado limpo** | secret com o kubeconfig do cluster alvo |
| `SLACK_WEBHOOK_URL` | a notificação de falha **no-op** (guardada por `env … != ''`) | webhook incoming do Slack |

Nenhum destes é exigido para "verde". **Regra inviolável:** nenhum material de secret entra em arquivo
versionado nem em log — todos vivem só como *repository secret*.

---

## 6. Escopo e garantia contínua

Este registro é uma **atestação pontual**, escopada aos commits citados — não uma alegação de verde
perpétuo. O **verde contínuo** dali para frente é garantido pela **branch protection** aplicada em
`master` (`harden-cicd-supply-chain`), que **exige** os checks `build` e `test` passando antes de
qualquer merge. Ver [`docs/ci-cd.md`](./ci-cd.md#supply-chain) para a esteira e o endurecimento.

<sub>Registro da change OpenSpec <code>validate-pipeline-live</code> · fluxo <em>spec-driven</em>.</sub>
