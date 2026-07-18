# 🔐 Runbook de Segurança — Rotação de credenciais e gestão de secrets

Procedimento operacional (_runbook_) para **rotacionar credenciais** e **gerir secrets** do EnergyHub,
parte da change `harden-security-credentials`. Cobre cada credencial da plataforma, o fluxo de
**Sealed Secrets / External Secrets**, o **backup/restore** da chave de selagem e a **guarda de
produção** que aborta o boot com credenciais placeholder.

> **Regra permanente do projeto:** as correções de segurança **precedem qualquer deploy não-local**.
> Nenhum valor real de credencial é commitado — em compose vive no `.env` (git-ignored); em Kubernetes
> vem de um `Secret` produzido por selagem/externalização (ver [`k8s/secrets/`](../k8s/secrets/)).

---

## 🧭 Mapa das credenciais

| Credencial | Onde é usada | Gerar com | Local (compose) | Local (k8s) |
| :--------- | :----------- | :-------- | :-------------- | :---------- |
| **`SECRET_KEY`** | Assinatura JWT — a **mesma** chave em todos os serviços (auth assina, os demais validam) | `openssl rand -hex 32` | `.env` → `SECRET_KEY` | Secret `energyhub-secret` chave `SECRET_KEY` |
| **Login admin** | Usuário `admin` semeado (bootstrap de RBAC) | `openssl rand -base64 24` | `.env` → `ADMIN_PASSWORD` | env de deploy da migração (`ADMIN_PASSWORD`/`ADMIN_PASSWORD_HASH`) |
| **Grafana admin** | Painel de observabilidade (compose) | `openssl rand -base64 24` | `.env` → `GRAFANA_ADMIN_PASSWORD` | — (Grafana só no compose) |
| **Senha Postgres** | Autenticação do banco (embutida nas `*_DATABASE_URL`) | `openssl rand -base64 24` | `.env` → `POSTGRES_PASSWORD` | Secret chave `POSTGRES_PASSWORD` + as `*_DATABASE_URL` |
| **Senha RabbitMQ** | Autenticação da mensageria (embutida em `RABBITMQ_URL`) | `openssl rand -base64 24` | `.env` → `RABBITMQ_PASSWORD` | Secret chave `RABBITMQ_PASSWORD` + `RABBITMQ_URL` |
| **`INTERNAL_API_KEY`** | Credencial inter-serviço das rotas `/internal/*` (header `X-Internal-Api-Key`) | `openssl rand -hex 32` | `.env` → `INTERNAL_API_KEY` | Secret chave `INTERNAL_API_KEY` |
| **Dashboard do Traefik** | Basic-auth do dashboard (`usuario:hash`, montado em `/etc/traefik-auth/users`) | `openssl passwd -apr1 '<senha>'` → `energyhub:<hash>` | — (k8s) | Secret chave `TRAEFIK_DASHBOARD_USERS` — **sem ela o pod do Traefik não sobe** |

> **Convenção de geração.** Chaves/tokens de alta entropia hexadecimais: `openssl rand -hex 32`
> (`SECRET_KEY`, `INTERNAL_API_KEY`). Senhas: `openssl rand -base64 24`. Cada credencial é
> **independente** — nunca reutilize uma única string entre `SECRET_KEY`, Postgres e RabbitMQ.

O `Secret` do Kubernetes se chama **`energyhub-secret`** (`type: Opaque`, namespace `energyhub`) e
carrega as chaves: `SECRET_KEY`, `INTERNAL_API_KEY`, `TRAEFIK_DASHBOARD_USERS`, `POSTGRES_PASSWORD`,
`RABBITMQ_PASSWORD`, `AUTH_DATABASE_URL`, `CLIENT_DATABASE_URL`, `CONTRACT_DATABASE_URL`,
`FINANCIAL_DATABASE_URL`, `AUDIT_DATABASE_URL` e `RABBITMQ_URL`.

---

## 🔁 Rotação por credencial

Cada procedimento segue o mesmo padrão: **(1) gerar** o valor novo → **(2) definir** onde vive
(`.env` no compose; o Secret selado/externalizado no k8s) → **(3) rolar** os serviços afetados.

### 🔑 `SECRET_KEY` (chave JWT compartilhada)

> ⚠️ **Rotacionar o `SECRET_KEY` invalida TODOS os tokens em circulação** (os JWTs assinados com a
> chave antiga deixam de validar). É um evento de **re-autenticação global**: todos os usuários
> precisam logar de novo. Por isso **role todos os serviços juntos** — auth, client, contract,
> financial e audit compartilham a chave; se um serviço ficar com a chave antiga e outro com a nova,
> a validação cruzada de JWT quebra.

1. **Gerar:** `openssl rand -hex 32`.
2. **Definir:**
   - _Compose:_ atualize `SECRET_KEY` no `.env`.
   - _Kubernetes:_ atualize a chave `SECRET_KEY` no `Secret` desselado e **re-sele** (ver
     [Fluxo Sealed/External Secrets](#-fluxo-sealed-secrets--external-secrets)).
3. **Rolar (todos de uma vez):**
   - _Compose:_ `docker compose up -d --force-recreate energyhub-api auth-service client-service contract-service financial-service audit-service`
     — inclui o **`energyhub-api`** (fachada monólito, que também embute `SECRET_KEY`/`DATABASE_URL`/`RABBITMQ_URL`);
     omiti-lo deixa o monólito com a credencial antiga. Vale o mesmo para as rotações de Postgres e RabbitMQ abaixo.
   - _Kubernetes:_
     ```bash
     for s in auth client contract financial audit; do
       kubectl rollout restart deployment/$s-service -n energyhub
     done
     kubectl rollout status deployment/auth-service -n energyhub
     ```

### 👤 Login admin (seed de bootstrap)

O usuário `admin` é semeado pela migração `0008_seed_data` a partir de um **secret de deploy** —
nunca de um hash commitado. Precedência: `ADMIN_PASSWORD_HASH` (hash bcrypt pronto) →
`ADMIN_PASSWORD` (texto, hasheado na migração com `bcrypt`, _rounds_ 12). Sem nenhum dos dois, o
admin **não é semeado** (nenhuma senha publicada é usada). A migração `0011_admin_password_rotation`
adiciona a coluna `require_password_rotation` e, **fora do perfil `development`**, marca o admin para
**trocar a senha no primeiro uso** — para a credencial de bootstrap não persistir.

1. **Gerar:** `openssl rand -base64 24` (senha em texto) — ou pré-compute o hash bcrypt e use
   `ADMIN_PASSWORD_HASH`.
2. **Definir** (variável de ambiente **do deploy da migração**, não de runtime do app):
   - _Compose/local:_ `ADMIN_PASSWORD` no `.env`. A rotação-no-primeiro-uso é dirigida por
     **`ENVIRONMENT`** (a migração `0011` só marca `require_password_rotation` fora de `development`) —
     **não** por `ADMIN_REQUIRE_PASSWORD_ROTATION`, que nenhum código lê (var vestigial no `.env.example`).
   - _Kubernetes:_ exporte `ADMIN_PASSWORD` (ou `ADMIN_PASSWORD_HASH`) e `ENVIRONMENT` no ambiente
     onde a migração `alembic upgrade head` roda (job/pod de migração), **não** no Secret de runtime.
3. **Rotação de uma conta já existente** (não é um re-seed): faça login e troque a senha pela API
   (o fluxo de _first-use rotation_ força isso quando `require_password_rotation = true`); ou, em
   quebra-de-vidro, atualize o hash direto no banco:
   ```bash
   # gerar hash bcrypt novo e aplicar em authdb (exemplo k8s)
   kubectl exec -n energyhub deploy/postgres -- \
     psql -U energyhub -d authdb -c \
     "UPDATE users SET password='<hash-bcrypt>', require_password_rotation=true WHERE username='admin';"
   ```
   Não há serviço a rolar — a mudança é de dado, lida na próxima autenticação.

### 📊 Grafana admin

Injetado pelo compose via `GF_SECURITY_ADMIN_USER`/`GF_SECURITY_ADMIN_PASSWORD` (Grafana não é
deployado em k8s — apenas no compose de observabilidade). Nunca `admin`/`admin`.

1. **Gerar:** `openssl rand -base64 24`.
2. **Definir:** `GRAFANA_ADMIN_USER` e `GRAFANA_ADMIN_PASSWORD` no `.env`.
3. **Rolar:** `docker compose up -d --force-recreate grafana`.
   > A variável só é aplicada na **criação** do usuário admin. Num Grafana já provisionado, troque
   > também pela UI (_Profile → Change Password_) ou via `grafana-cli admin reset-admin-password`,
   > pois o volume `grafana_data` persiste o usuário.

### 🐘 Senha do PostgreSQL

A senha é embutida nas `*_DATABASE_URL` (um banco por serviço). Rotacioná-la exige **trocar a senha
no servidor** e **atualizar todas as URLs**.

1. **Gerar:** `openssl rand -base64 24`.
2. **Trocar no servidor** (o Postgres não relê a senha de env após o initdb):
   ```bash
   # compose
   docker exec -it energyhub-postgres \
     psql -U energyhub -c "ALTER USER energyhub WITH PASSWORD '<nova-senha>';"
   # k8s
   kubectl exec -n energyhub deploy/postgres -- \
     psql -U energyhub -c "ALTER USER energyhub WITH PASSWORD '<nova-senha>';"
   ```
3. **Definir:**
   - _Compose:_ `POSTGRES_PASSWORD` no `.env` (o compose remonta as `DATABASE_URL` com `${POSTGRES_PASSWORD}`).
   - _Kubernetes:_ atualize `POSTGRES_PASSWORD` **e** as cinco `*_DATABASE_URL` no Secret desselado e
     **re-sele**.
4. **Rolar:** os 5 serviços (mesma sequência do `SECRET_KEY`) para relerem as URLs novas.

### 🐰 Senha do RabbitMQ

Embutida em `RABBITMQ_URL`. Desde `fix-microservices-gaps`, **os 5 serviços** usam RabbitMQ —
auth/client/contract/financial publicam eventos de auditoria e o audit consome.

1. **Gerar:** `openssl rand -base64 24`.
2. **Trocar no broker** (usuário já criado não relê `RABBITMQ_DEFAULT_PASS`):
   ```bash
   docker exec -it energyhub-rabbitmq rabbitmqctl change_password energyhub '<nova-senha>'
   # k8s: kubectl exec -n energyhub deploy/rabbitmq -- rabbitmqctl change_password energyhub '<nova-senha>'
   ```
3. **Definir:**
   - _Compose:_ `RABBITMQ_PASSWORD` no `.env`.
   - _Kubernetes:_ atualize `RABBITMQ_PASSWORD` **e** `RABBITMQ_URL` no Secret desselado e **re-sele**.
4. **Rolar:** os **5 serviços** (todos usam RabbitMQ — publicam eventos de auditoria / consomem).

### 🔗 `INTERNAL_API_KEY` (credencial inter-serviço)

Segredo compartilhado exigido nas rotas `/internal/*` (o auth expõe lookups internos; os demais
chamam com o header `X-Internal-Api-Key`). É defesa-em-profundidade **junto** com a NetworkPolicy —
todos os serviços precisam do **mesmo** valor, então trate como o `SECRET_KEY`: role todos juntos.

1. **Gerar:** `openssl rand -hex 32`.
2. **Definir:**
   - _Compose:_ `INTERNAL_API_KEY` no `.env`.
   - _Kubernetes:_ atualize a chave `INTERNAL_API_KEY` no Secret desselado e **re-sele**.
3. **Rolar:** os 5 serviços de uma vez (chamador e chamado precisam concordar no valor). Uma
   defasagem transitória durante o rollout faz o `/internal` responder `401/403` até todos os pods
   estarem na chave nova — role e aguarde `rollout status` antes de considerar concluído.

---

## 🛡️ Fluxo Sealed Secrets / External Secrets

Objetivo: **nenhum material de secret em texto plano** vai ao repositório. O artefato commitado é
**criptografado** (`SealedSecret`) ou **externalizado** (`ExternalSecret` referenciando um cofre); o
controlador materializa o `energyhub-secret` real dentro do cluster. Os consumidores
(`valueFrom.secretKeyRef`) não mudam — as chaves resolvidas são idênticas às contratadas.

### Opção A — Sealed Secrets (padrão) 🔒

O repositório já traz o ferramental — prefira-o ao `kubeseal` na mão (ver
[`k8s/secrets/README.md`](../k8s/secrets/README.md) e [`sealed-secrets-controller.md`](../k8s/secrets/sealed-secrets-controller.md)):

```bash
# 1) Preencher o Secret DESSELADO (nunca commitado) a partir do template versionado:
cp k8s/secrets/energyhub-secret.local.example.yaml k8s/secrets/energyhub-secret.local.yaml
#    edite k8s/secrets/energyhub-secret.local.yaml trocando cada REPLACE_ME_* pelos valores frescos
#    (o .local.yaml é gitignored).

# 2) Selar → gera k8s/secrets/energyhub-sealedsecret.yaml (commitável). O script recusa selar
#    enquanto restar algum REPLACE_ME e usa --controller-name sealed-secrets-controller + --scope strict.
bash k8s/secrets/seal-secrets.sh

# 3) Aplicar o SealedSecret (isto SIM vai ao git — só o controlador consegue decriptar).
kubectl apply -f k8s/secrets/energyhub-sealedsecret.yaml

# 4) O controlador materializa o Secret `energyhub-secret` no namespace energyhub.
kubectl get secret energyhub-secret -n energyhub
```

> _Fallback manual_ (sem o script): edite uma cópia local e sele com
> `kubeseal --controller-name sealed-secrets-controller --format yaml < cópia.yaml > k8s/secrets/energyhub-sealedsecret.yaml`,
> depois **`shred -u`** a cópia. Não use `--controller-namespace kube-system` sozinho — o `kubeseal`
> procura o serviço pelo **nome** `sealed-secrets-controller`.

O `SealedSecret` é cifrado **assimetricamente** e amarrado ao _scope_ `name`+`namespace`
(`energyhub-secret`/`energyhub`) — só o controlador daquele cluster o decripta. Para **rotacionar**
uma credencial, repita: edite o desselado, re-sele, `kubectl apply`, role os serviços.

### Opção B — External Secrets Operator + Vault 🗄️

Para times que já operam um cofre. Em vez de commitar o valor cifrado, commita-se um `ExternalSecret`
que **aponta** para o segredo no store:

1. Grave os valores frescos no Vault (ex.: `vault kv put secret/energyhub SECRET_KEY=… POSTGRES_PASSWORD=…`).
2. Configure um `SecretStore`/`ClusterSecretStore` apontando para o Vault (auth via token/k8s).
3. Commite um `ExternalSecret` cujo `target.name: energyhub-secret` mapeia cada `data.remoteRef`
   (`SECRET_KEY`, `POSTGRES_PASSWORD`, … `INTERNAL_API_KEY`) para as chaves do Secret.
4. O operador materializa e **mantém sincronizado** o `energyhub-secret`; rotacionar = atualizar o
   valor no Vault (o operador propaga no `refreshInterval`) e rolar os serviços.

Em ambos os caminhos as **chaves do Secret são idênticas** — trocar A↔B não bifurca os manifestos de
Deployment.

---

## 💾 Backup e restore da chave de selagem / material do cofre

> **O perigo operacional é PERDER a chave, não vazá-la.** Vazar exige rotação; **perder** torna
> **todos os `SealedSecret` do repositório irrecuperáveis** — sem a chave privada, nada os decripta e
> você teria de reinstalar o controlador (nova chave) e **re-selar tudo do zero** a partir dos valores
> originais. Trate o backup da chave como pré-requisito de produção.

### Sealed Secrets — chave privada do controlador

A chave privada vive num `Secret` no namespace do controlador (tipicamente `kube-system`), rotulado
`sealedsecrets.bitnami.com/sealing-key=active`.

```bash
# BACKUP — exporte a(s) chave(s) ativa(s) e guarde FORA do repositório (cofre offline, cifrado).
kubectl get secret -n kube-system \
  -l sealedsecrets.bitnami.com/sealing-key=active \
  -o yaml > sealed-secrets-key.backup.yaml
#   → mova para armazenamento seguro (ex.: gestor de segredos corporativo / cofre físico).
#   → NUNCA commite este arquivo. Ele decripta todos os SealedSecrets.

# RESTORE — num cluster novo/recriado, reaplique a chave ANTES dos SealedSecrets e reinicie o controlador.
kubectl apply -f sealed-secrets-key.backup.yaml
kubectl delete pod -n kube-system -l name=sealed-secrets-controller   # força recarregar a chave
```

Após o restore, os `SealedSecret` existentes voltam a ser decriptáveis e o controlador re-materializa
`energyhub-secret`.

### External Secrets / Vault — material de unseal/root

O que precisa de backup é o **material do cofre**, não um Secret do cluster:

- **Unseal keys** (ou as _shares_ Shamir) e o **root token** do Vault — guarde as _shares_
  **distribuídas** entre custodiantes distintos (quebra-de-vidro), offline e cifradas.
- O **storage backend** do Vault (Raft/Consul/etc.) — backup regular (`vault operator raft snapshot save`).
- Perder as unseal keys **sela o cofre permanentemente**: os `ExternalSecret` deixam de resolver e o
  `energyhub-secret` para de sincronizar. Mesmo princípio: perder é irreversível; testar o restore é
  obrigatório.

---

## 🚨 Guarda de credenciais de produção

Quando `environment == "production"`, o app **aborta o boot** (`InsecureCredentialError`, _fail-fast_)
se qualquer credencial obrigatória estiver **vazia/ausente** ou contiver um **placeholder conhecido**.
Fora de produção (`development`/`staging`/local) a checagem é **no-op** — perfis locais seguem
permissivos com valores de conveniência do `.env`/compose.

- **Variáveis checadas** (`config/settings.py` → `config/security_guard.py`):
  `SECRET_KEY`, `DATABASE_URL`, `RABBITMQ_URL`.
- **Conjunto de placeholders proibidos** (`KNOWN_PLACEHOLDERS`):
  `change-me-in-production`, `energyhub123`, `admin`, `ChangeMe123!`.
- A guarda rejeita **apenas** esse conjunto explícito + valores vazios — **nunca** "senhas fracas"
  arbitrárias — para não bloquear um boot legítimo por falso-positivo.
- No `docker-compose.yml`, as variáveis são lidas com `${VAR:?...}`: se faltarem, o boot falha **em
  qualquer perfil** (camada complementar à guarda de produção).

> Se o boot em produção abortar, a mensagem nomeia a credencial ofensora. Rotacione e forneça o valor
> real via Secret/variável de ambiente (ver seções acima e o `.env.example`).

---

## ✅ Checklist pré-produção

Antes de qualquer deploy não-local, confirme:

- [ ] **Rotacionar todas as credenciais** — `SECRET_KEY`, login admin, Grafana, Postgres, RabbitMQ,
      `INTERNAL_API_KEY` — com valores frescos e **distintos**; nenhum placeholder conhecido
      (`change-me-in-production`, `energyhub123`, `admin`, `ChangeMe123!`) permanece ativo.
- [ ] **Selar os secrets** — o `energyhub-secret` vem de um `SealedSecret`/`ExternalSecret`; **nenhum**
      material de secret em texto plano no repositório; a chave de selagem/material do cofre está
      **backupeada fora do repo** e o restore foi testado.
- [ ] **Trancar as superfícies internas/admin** — `/internal/*` exige `INTERNAL_API_KEY` e fica fora
      do gateway público; dashboard do Traefik com `insecure` **desligado** e autenticação; UI do
      Consul não exposta / restrita.
- [ ] **TLS na borda** — cert-manager emite o certificado, o `Ingress` termina HTTPS e redireciona
      HTTP→HTTPS.
- [ ] **Aplicar NetworkPolicies** — _default-deny_ no namespace + regras _allow_ de menor privilégio
      (só as dependências declaradas de cada serviço).
- [ ] `ENVIRONMENT=production` definido — a guarda de credenciais está **ativa** e o boot foi validado.

---

<sub>Voltar ao <a href="./README.md">índice da documentação</a> · secrets: <a href="../k8s/secrets/">k8s/secrets/</a> · variáveis: <a href="../.env.example">.env.example</a>.</sub>
