# 🔐 `k8s/secrets/` — Gestão de segredos sem plaintext no repositório

Antes, `k8s/secret.yaml` era um `Secret` com `stringData` em **texto puro** versionado no git — um
`Secret` do Kubernetes é apenas **base64**, não criptografia, então qualquer pessoa com acesso ao
repositório lia `SECRET_KEY`, senhas e as `*_DATABASE_URL` (que embutem a senha do Postgres). Este
diretório substitui esse arquivo por um fluxo em que **o artefato commitado nunca contém o valor em
claro** — o segredo real só existe cifrado (SealedSecret) ou fora do git (Vault via ExternalSecret) e
é **resolvido dentro do cluster** para o `Secret` Opaque `energyhub-secret` que os Deployments já
consomem.

> A forma final continua sendo o `Secret` `energyhub-secret` (namespace `energyhub`). As chaves
> resolvidas **devem ser idênticas** às referenciadas pelos Deployments — mudar um nome de chave aqui
> quebra o `secretKeyRef` de todos os serviços.

---

## 🗂️ Arquivos deste diretório

| Arquivo | Commitado? | Papel |
| :------ | :--------- | :---- |
| `energyhub-secret.local.example.yaml` | ✅ sim | Template UNSEALED (`kind: Secret`) com placeholders `REPLACE_ME_*`. Ponto de partida do operador. |
| `energyhub-secret.local.yaml` | ❌ **NÃO** (gitignored) | Cópia do template acima **preenchida com valores reais**. Insumo do `kubeseal`. Nunca é commitada. |
| `energyhub-sealedsecret.yaml` | ✅ sim | Saída cifrada do `kubeseal` — este é o artefato que vai para o cluster (default). |
| `seal-secrets.sh` | ✅ sim | Roda `kubeseal` sobre o `.local.yaml` e gera o `energyhub-sealedsecret.yaml`. |
| `energyhub-externalsecret.example.yaml` | ✅ sim | Alternativa: `SecretStore` (Vault) + `ExternalSecret` que materializa `energyhub-secret`. |
| `sealed-secrets-controller.md` | ✅ sim | Versão fixada e comando de instalação do controlador Sealed Secrets. |
| `create-ghcr-pull-secret.sh` | ✅ sim | Cria o `ghcr-pull-secret` (credencial de **pull** das imagens privadas do GHCR). Ver §🐳. |
| `ghcr-pull-sealedsecret.yaml` | ✅ sim *(se gerado)* | Saída de `create-ghcr-pull-secret.sh --seal` — pull secret cifrado, para GitOps. |

> **Dois segredos, papéis distintos.** `energyhub-secret` é o que a aplicação **consome em runtime**
> (JWT, senhas, URLs). `ghcr-pull-secret` é o que o **kubelet** usa **antes** do container existir,
> para baixar a imagem. Um serviço com o `energyhub-secret` perfeito e sem o `ghcr-pull-secret`
> nunca chega a rodar — trava em `ImagePullBackOff`.

---

## 🔑 Chaves do `energyhub-secret` (contrato — mantenha idênticas aos Deployments)

Todos os serviços referenciam estas chaves via `secretKeyRef` para `name: energyhub-secret`:

- `SECRET_KEY` — chave de assinatura JWT (a MESMA em todos os serviços; auth assina, os demais validam).
- `INTERNAL_API_KEY` — segredo compartilhado das chamadas serviço-a-serviço (`/internal`, forwardAuth).
- `TRAEFIK_DASHBOARD_USERS` — htpasswd (`usuario:hash`) do basic-auth do dashboard do Traefik,
  projetado como arquivo em `/etc/traefik-auth/users`. **Sem esta chave o pod do Traefik nao sobe.**
- `POSTGRES_PASSWORD`, `RABBITMQ_PASSWORD` — senhas dos backends stateful.
- `AUTH_DATABASE_URL`, `CLIENT_DATABASE_URL`, `CONTRACT_DATABASE_URL`, `FINANCIAL_DATABASE_URL`,
  `AUDIT_DATABASE_URL` — um banco por serviço (database-per-service), com a senha **embutida** na URL.
- `RABBITMQ_URL` — URL de mensageria com credencial embutida.

---

## 🧪 1) Gerar valores fortes

```bash
# SECRET_KEY e INTERNAL_API_KEY — 32 bytes em hex (64 chars)
openssl rand -hex 32

# Senhas (POSTGRES_PASSWORD / RABBITMQ_PASSWORD) — 24 bytes em base64
openssl rand -base64 24
```

Copie o template e preencha os valores (o arquivo `*.local.yaml` é **gitignored**):

```bash
cp k8s/secrets/energyhub-secret.local.example.yaml k8s/secrets/energyhub-secret.local.yaml
# edite k8s/secrets/energyhub-secret.local.yaml, trocando cada REPLACE_ME_* pelo valor gerado.
# a mesma senha do Postgres deve aparecer em POSTGRES_PASSWORD e dentro de cada *_DATABASE_URL.
```

---

## 🅰️ Fluxo padrão — Sealed Secrets (Bitnami)

O controlador Sealed Secrets guarda um par de chaves **dentro do cluster**. O `kubeseal` cifra o
`Secret` com a chave **pública** do controlador; só o controlador (com a privada) consegue decifrar,
já dentro do cluster, produzindo o `Secret` `energyhub-secret`. O `SealedSecret` cifrado é seguro
para commitar.

```bash
# 1. Instalar o controlador (ver sealed-secrets-controller.md p/ a versão fixada).
# 2. Selar o Secret preenchido → gera k8s/secrets/energyhub-sealedsecret.yaml:
bash k8s/secrets/seal-secrets.sh

# 3. Aplicar o SealedSecret cifrado (o controlador o expande em energyhub-secret):
kubectl apply -f k8s/secrets/energyhub-sealedsecret.yaml
kubectl get secret energyhub-secret -n energyhub   # criado pelo controlador

# 4. Aplicar o restante da plataforma normalmente:
kubectl apply -f k8s/
```

> O `SealedSecret` é fixado a `namespace + name` (escopo `strict`, padrão). Ele só decifra como
> `energyhub-secret` no namespace `energyhub` — não pode ser reusado em outro namespace/nome.

---

## 🅱️ Alternativa — External Secrets Operator (Vault)

Em vez de cifrar e commitar, mantenha os valores **fora do git**, em um HashiCorp Vault. O External
Secrets Operator lê o Vault e **materializa** o `Secret` `energyhub-secret` no cluster, mantendo-o
sincronizado (`refreshInterval`). Nada sensível — nem cifrado — fica no repositório; só o mapeamento.

```bash
# Pré-requisito: External Secrets Operator instalado e um Vault acessível pelo cluster.
# (helm repo add external-secrets https://charts.external-secrets.io && helm install ...)

# Popular o Vault (KV v2) com os mesmos valores gerados acima, ex.:
vault kv put secret/energyhub/platform \
  SECRET_KEY="..." INTERNAL_API_KEY="..." POSTGRES_PASSWORD="..." RABBITMQ_PASSWORD="..." \
  AUTH_DATABASE_URL="..." CLIENT_DATABASE_URL="..." CONTRACT_DATABASE_URL="..." \
  FINANCIAL_DATABASE_URL="..." AUDIT_DATABASE_URL="..." RABBITMQ_URL="..."

# Aplicar SecretStore + ExternalSecret (materializa energyhub-secret):
kubectl apply -f k8s/secrets/energyhub-externalsecret.example.yaml
kubectl get secret energyhub-secret -n energyhub   # criado pelo operador
```

---

## 🐳 `ghcr-pull-secret` — puxar as imagens privadas do GHCR

As 5 imagens são publicadas em `ghcr.io/siquaradev/energyhub-<serviço>-service` e **nascem
privadas** — um `GET` anônimo no manifest devolve `401`. Um cluster real não tem `docker login`
nenhum, então sem credencial o kubelet falha o pull e **todo serviço fica em `ImagePullBackOff`**.

O fluxo tem duas peças:

| Peça | O quê |
| :--- | :---- |
| `ghcr-pull-secret` | `kubernetes.io/dockerconfigjson` com o token do GHCR. **Não versionado** (embute o token em claro). |
| [`k8s/serviceaccount.yaml`](../serviceaccount.yaml) | SA `energyhub-sa` que referencia o Secret. Os 5 Deployments apontam para ele via `serviceAccountName` — um único ponto de verdade. |

```bash
# Token: PAT CLÁSSICO com escopo read:packages e NADA MAIS. Se o cluster for comprometido, um
# token só-leitura de imagens é o menor estrago possível. Nunca use write:packages ou repo aqui.
export GHCR_USERNAME=SiquaraDev
export GHCR_TOKEN=ghp_xxx

bash k8s/secrets/create-ghcr-pull-secret.sh          # cria/atualiza direto no cluster (idempotente)
bash k8s/secrets/create-ghcr-pull-secret.sh --seal   # OU: gera um SealedSecret cifrado p/ GitOps

# Conferir o wiring (deve listar ghcr-pull-secret):
kubectl -n energyhub get serviceaccount energyhub-sa -o jsonpath='{.imagePullSecrets}'
```

> **Rotação.** Rodar o script de novo atualiza o Secret, mas os pods **já rodando** seguem com a
> imagem que já baixaram. Para revalidar o pull:
> `kubectl -n energyhub rollout restart deployment -l app.kubernetes.io/part-of=energyhub`.

<a id="pacotes-publicos"></a>

### 🔀 Alternativa: tornar os pacotes públicos

Dá para dispensar o pull secret **inteiro** publicando as imagens como públicas
(GitHub → Packages → *Package settings* → *Change visibility* → Public), e então removendo o bloco
`imagePullSecrets` de `k8s/serviceaccount.yaml`. Sem credencial, sem rotação, sem preflight.

**O trade-off, honestamente:**

| | Pull secret (privado) — **padrão** | Pacote público |
| :-- | :-- | :-- |
| Quem baixa a imagem | só quem tem o token | qualquer pessoa na internet |
| Operação | criar + rotacionar o token | zero |
| Preflight/probe do CD | exercita o caminho autenticado real | não exercita nada |

> **Sem exagero:** este repositório é **público**, então o código-fonte já é legível por qualquer um
> — publicar as imagens **não** vazaria "o código". O que a imagem acrescenta é o artefato
> **construído**: a árvore exata de dependências e suas versões (um mapa de CVEs pronto para quem
> for procurar), além de qualquer coisa embutida em build. É um delta modesto, não uma catástrofe.

O motivo real de manter **privado** como padrão não é sigilo — é que ele **força o caminho de
produção a ser exercitado**. Com o pacote público, o pull secret, o SA e os preflights nunca são
testados; no dia em que um serviço realmente precisar de registry autenticado (imagem de cliente,
mirror interno, migração para ECR/Artifact Registry), a plataforma descobre em produção que essa
trilha nunca funcionou. Vá de **público** num demo descartável em que essa trilha não interessa.

---

## 🚫 Regras invioláveis

- **Nunca** commitar `energyhub-secret.local.yaml` (nem qualquer `*.local.yaml`) — é o `Secret` em
  claro. O `.gitignore` da raiz já o bloqueia; confira com `git status` antes de commitar.
- **Nunca** recriar o antigo `k8s/secret.yaml` com valores em claro.
- **Nunca** commitar um `dockerconfigjson` preenchido: `base64` **não é cifra** e o token do GHCR
  sai legível. Use `create-ghcr-pull-secret.sh` (o token só transita pelo ambiente) ou `--seal`.
- Ao adicionar/renomear uma chave, atualize **os três** pontos em conjunto: este README, o
  template `*.example.yaml`, o `ExternalSecret` **e** os `secretKeyRef` dos Deployments.
- Rotacionar `SECRET_KEY`, `INTERNAL_API_KEY` e as senhas periodicamente e após qualquer exposição.
