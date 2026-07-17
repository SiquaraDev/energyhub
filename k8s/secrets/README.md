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

## 🚫 Regras invioláveis

- **Nunca** commitar `energyhub-secret.local.yaml` (nem qualquer `*.local.yaml`) — é o `Secret` em
  claro. O `.gitignore` da raiz já o bloqueia; confira com `git status` antes de commitar.
- **Nunca** recriar o antigo `k8s/secret.yaml` com valores em claro.
- Ao adicionar/renomear uma chave, atualize **os três** pontos em conjunto: este README, o
  template `*.example.yaml`, o `ExternalSecret` **e** os `secretKeyRef` dos Deployments.
- Rotacionar `SECRET_KEY`, `INTERNAL_API_KEY` e as senhas periodicamente e após qualquer exposição.
