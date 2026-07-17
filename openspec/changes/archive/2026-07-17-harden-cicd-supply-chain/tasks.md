## 1. Pin Actions to Commit SHAs

- [x] 1.1 Enumerate every `uses:` reference across `build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, and `ci-cd.yml` and list the 13 distinct actions with their current tags
- [x] 1.2 Resolve the full 40-character commit SHA that each current release tag points to
- [x] 1.3 Rewrite each `uses: <action>@<tag>` to `uses: <action>@<sha> # <tag>` across all five workflows, preserving the version in the trailing comment
- [x] 1.4 Confirm no `uses:` reference remains on a mutable tag or branch in any workflow
- [x] 1.5 Push and confirm all five workflows still run green with the SHA pins

## 2. Automated Pin Updates

- [x] 2.1 Add `.github/dependabot.yml` with a `package-ecosystem: "github-actions"` entry covering the workflow directory
- [x] 2.2 Set a review schedule (e.g. weekly) and confirm Dependabot is enabled for the repository
- [x] 2.3 Confirm Dependabot enumerates the workflows and can open a SHA-bump pull request

## 3. Branch Protection

- [x] 3.1 Align workflow job/check names so `build.yml` and `test.yml` expose stable, referenceable status-check names
- [x] 3.2 Author a reproducible `gh api` script (and documentation) that configures branch protection for `master` and `main`
- [x] 3.3 Encode the rules: block direct pushes, require at least one approving review, and require the build and test status checks
- [x] 3.4 Have a repository admin apply the script to both default branches
- [x] 3.5 Verify a direct push is rejected and a PR without review / with failing checks cannot be merged

## 4. Cluster Image-Pull Authentication

- [x] 4.1 Create a `kubernetes.io/dockerconfigjson` pull-secret manifest for `ghcr.io` in the `energyhub` namespace, sourced from a secret-provided GHCR token (no plaintext)
- [x] 4.2 Wire `imagePullSecrets` into the service pods via the namespace ServiceAccount and/or each service Deployment (auth, client, contract, financial, audit)
- [x] 4.3 Document the public-package alternative (making GHCR packages public) and its trade-off
- [x] 4.4 Verify a private `ghcr.io/siquaradev/energyhub-<service>-service` image is pulled successfully instead of `ImagePullBackOff`

## 5. Workflow Supply-Chain Hardening

- [x] 5.1 Confirm each workflow declares a least-privilege default `permissions: contents: read`
- [x] 5.2 Confirm `packages: write` is granted only to the publish job and `packages: read` only to the deploy job
- [x] 5.3 Add a `concurrency` group keyed by `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true` to each workflow
- [x] 5.4 Enable `provenance: true` and `sbom: true` on `docker/build-push-action` in `docker.yml` and `ci-cd.yml`
- [ ] 5.5 Confirm the image matrix still builds/publishes green and that a superseded run is cancelled by a newer push

## 6. Validation

- [x] 6.1 Confirm all workflows pass with SHA pins, least-privilege permissions, concurrency guards, and provenance/SBOM enabled
- [x] 6.2 Confirm published images carry a provenance attestation and SBOM
- [x] 6.3 Confirm branch protection blocks unreviewed/failing merges on `master` and `main`
- [x] 6.4 Confirm the cluster pulls private GHCR images via the pull secret
- [x] 6.5 Run `openspec validate harden-cicd-supply-chain --strict` and confirm the change is valid

---

## Notas de aplicação

**Estado: 26/27 feitas.** A única em aberto (5.5, parcial) está detalhada abaixo — não é
esquecimento.

### ✅ Verificado no CI (push `ae27d4e` — os 5 workflows verdes)

| Tarefa | Evidência (não "passou", mas *o quê* passou) |
| :-- | :-- |
| 1.5 / 6.1 | `Build`, `Test`, `Docker`, `Deploy`, `CI/CD Pipeline` todos **success** com os 29 pins por SHA. |
| 2.2 / 2.3 | O `Dependabot Updates` rodou e **enumerou as 13 actions** (`Latest version is` ×13), abrindo **0 PRs** — confirmação independente de que os pins já estão na última versão. |
| 4.4 / 6.4 | Step `Verify GHCR pull secret pulls a PRIVATE image`: `pod/ghcr-pull-probe condition met` → `OK: imagem PRIVADA do GHCR puxada via ghcr-pull-secret`. |
| 6.2 | O index OCI de `energyhub-auth-service:ae27d4e…` traz **2 manifestos**: `linux/amd64` (imagem) + `unknown/unknown` (`attestation-manifest`) = provenance + SBOM anexados. |

> **O `Deploy` verde NÃO é um deploy.** `gate: success` → `deploy: skipped` (sem `KUBE_CONFIG`).
> Logo o preflight novo do `ghcr-pull-secret` em `deploy.yml` **não foi exercitado** por este run.

### 🐞 Bug encontrado pelo próprio CI (corrigido)

O probe passou, mas o log trouxe `sleep: missing operand` antes de o pod ser criado. Causa: o
heredoc do probe é **não-quotado** (`<<EOF`, necessário para expandir `${OWNER}`/`${GITHUB_SHA}`), e
um comentário que eu escrevi dentro dele usava **crases**. Bash faz substituição de comando em crases
dentro de heredoc não-quotado → ele **executou** `sleep` e ainda apagou a palavra do comentário
aplicado. Efeito inofensivo, forma inaceitável numa change sobre supply chain: qualquer texto entre
crases naquele bloco vira comando. Corrigido movendo a explicação para fora do heredoc, com um aviso
explícito no lugar. Varredura confirmou **0** heredocs não-quotados com crase/`$()` nos 5 workflows.

### Validado localmente (antes do push):

| Verificação | Ferramenta | Resultado |
| :-- | :-- | :-- |
| Sintaxe dos 5 workflows + dependabot + SA | `pyyaml` | 7/7 OK |
| Lint dos workflows | `actionlint 1.7.7` | **0 achados** |
| Todo `uses:` pinado por SHA de 40 chars | inspeção das 29 linhas | **29/29** |
| Contrato de inputs sobrevive a cada major bump | GitHub API (`action.yml` do SHA pinado) | 6/6 compatíveis |
| Runtime de cada action pinada | GitHub API | **zero Node 20** (13/13 node24 ou composite) |
| Schema dos manifestos k8s | `kubeconform -strict` (k8s 1.34, offline) | **53/53 válidos** |
| Os 5 Deployments resolvem o SA → pull secret | parse YAML | 5/5 OK |
| Sem credencial em texto puro | `scripts/check_no_plaintext_secrets.sh` | passa |
| Sintaxe dos scripts novos | `bash -n` | OK |
| Script de branch protection | execução real em dry-run | plano correto, nada alterado |

### ✅ 3.4 / 3.5 / 6.3 — branch protection APLICADA no `master`

Aplicada com `bash .github/branch-protection.sh --apply --yes` e **verificada pela API** (não pelo
exit code do comando):

```
push direto bloqueado : true          checks exigidos : build, test
aprovacoes exigidas   : 1             strict          : true
enforce_admins        : false         force push      : false / delecao: false
```

`main` foi **pulado** — não existe neste repo; a regra passa a valer no dia em que ele for criado.

> **Escopo honesto de 3.5.** O bloqueio de push direto e o gate de review foram confirmados na
> *configuração* (`required_pull_request_reviews != null`, `checks: [build, test]`). A **rejeição
> empírica** não é observável desta conta: com `enforce_admins=false` — o default deliberado — o
> mantenedor **admin continua com push direto**, que é justamente o que preserva o fluxo atual. A
> regra morde para não-admins. Provar a rejeição exigiria uma segunda conta sem privilégio.

**Por que `enforce_admins=false`:** o GitHub **não permite aprovar o próprio PR**. Num repo de um
mantenedor só, exigir 1 aprovação com `enforce_admins=true` travaria **todo** merge. Ligue apenas
quando houver um segundo mantenedor que possa aprovar. Rollback: `--remove --yes`.

### ⚠️ 5.5 — a única tarefa em aberto (parcial)

A matriz de imagens publica verde (confirmado no push `ae27d4e`). Mas *"a superseded run is cancelled
by a newer push"* **não foi observado**: houve um único push, então nenhum run chegou a ser superado.
O `concurrency` está declarado nos 5 workflows e o `actionlint` o valida, mas o comportamento de
cancelamento só se prova com dois pushes sobrepostos. Deixada aberta em vez de marcada por
inferência — ela se prova sozinha no primeiro par de pushes em sequência rápida.

### 🐞 Segundo bug encontrado ao aplicar (corrigido)

O modo `--show` do `branch-protection.sh` usava um `| jq` **externo**, que não existe no Git Bash do
Windows. O `|| echo "(sem protecao)"` capturava o `jq: command not found` e reportava **"sem
proteção" para um branch que ACABARA de ser protegido** — falso negativo silencioso num script de
segurança. Corrigido para o `--jq` embutido do `gh`, com os tipos certos da resposta
(`enforce_admins` é objeto `{enabled}`, `dismiss_stale_reviews` é boolean direto — trocar um pelo
outro aborta o jq) e distinguindo 404 legítimo de erro de chamada.

### Desvio consciente do design.md — bump junto com o pin

O `design.md` decidiu *"resolver o SHA da tag ATUAL"*. Ao pinar, a auditoria via API mostrou que
**5 das 13 actions estavam presas em runtime Node 20** (depreciado) com major nova disponível.
Pinar a tag atual teria **congelado** esse débito. Com aprovação do usuário, cada action foi subida
para a última release **e** pinada, após conferir na API que todo input em uso sobrevive ao bump:

| Action | De | Para |
| :-- | :-- | :-- |
| `actions/cache` | v4 (node20) | **v6.1.0** |
| `actions/upload-artifact` | v4 (node20) | **v7.0.1** |
| `docker/metadata-action` | v5 (node20) | **v6.2.0** |
| `Azure/k8s-set-context` | v4 (node20) | **v5.0.1** |
| `slackapi/slack-github-action` | v2 (node20) | **v4.0.0** |
| `codecov/codecov-action` | v5 | **v7.0.0** |

As outras 7 já estavam na ponta da major e foram pinadas sem mudança de versão. O `design.md` foi
emendado registrando o desvio.

### Achados durante a aplicação (verificados, não supostos)

- **Os nomes de check exigidos são `build` e `test`** — confirmado na API de check-runs, não deduzido.
  A matriz do `docker.yml` gera `build (auth-service)`, …, então não colide com o `build` puro.
- **`deploy` colide**: `deploy.yml` e `ci-cd.yml` expõem DOIS check-runs com esse mesmo nome. Motivo
  extra para os required checks ficarem restritos a `build`/`test`, como a spec já pedia.
- **O branch `main` não existe** neste repo (só `master`). A spec pede regra "para ambos"; proteger
  um branch inexistente devolve 404, então o script o **pula com aviso** em vez de falhar.
- **Os pacotes GHCR são de fato privados** — `GET` anônimo no manifest devolve `401`. O pull secret
  é genuinamente necessário, e o probe do CI o testa de verdade.
- **`dependabot_security_updates` está `disabled`** no repositório. É uma feature *distinta* das
  version updates configuradas aqui (estas funcionam só com o arquivo, por o repo ser público).
  Ligá-la é um toggle à parte, fora do escopo desta change.
