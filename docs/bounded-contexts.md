# 🧩 Bounded Contexts — EnergyHub (Fase 15)

Este documento registra a **decomposição do monólito modular** (Fases 2–14) em **contextos
delimitados** (_bounded contexts_) e o **grafo de dependências** que dirige a extração em
microsserviços. É o artefato durável que fundamenta a Fase 15.

> 📌 A Fase 15 extrai **5 dos 8 contextos** — Auth, Clients, Contracts, Financial e Audit — que
> ancoram o grafo e exercitam todos os padrões (discovery, comunicação HTTP, resiliência, gateway).
> Negotiations, Notifications e Reports seguem o mesmo _blueprint_ em fases posteriores.

---

## 1. Inventário: módulo → contexto → serviço

Cada módulo do monólito (`src/energyhub/<módulo>/`) mapeia para **exatamente um** contexto, dono dos
seus dados e comportamento. Nenhum módulo fica sem dono nem é dividido entre dois serviços.

| Módulo (monólito) | Contexto | Serviço-alvo | Porta | Extraído na Fase 15? |
| :---------------- | :------- | :----------- | :---: | :------------------: |
| `auth` | **Auth** — identidade, RBAC | `auth-service` | 8001 | ✅ |
| `clients` | **Clients** — clientes + contatos | `client-service` | 8002 | ✅ |
| `contracts` | **Contracts** — contratos de energia | `contract-service` | 8003 | ✅ |
| `financial` | **Financial** — faturas + pagamentos | `financial-service` | 8004 | ✅ |
| `audit` | **Audit** — trilha de auditoria | `audit-service` | 8005 | ✅ |
| `negotiations` | **Negotiations** — negociações + transações | `negotiation-service` | 8006 | 📋 depois |
| `notifications` | **Notifications** — notificações | `notification-service` | 8007 | 📋 depois |
| `reports` | **Reports** — relatórios/agregação | `report-service` | 8008 | 📋 depois |

---

## 2. Responsabilidades por contexto

- **Auth** — usuários, papéis e permissões; emissão/validação de JWT; RBAC. **Dono da verdade** sobre
  identidade. Não depende de ninguém (raiz do grafo).
- **Clients** — clientes (CNPJ, razão social, endereço) e seus contatos. Valida o usuário criador via
  Auth. Dono da verdade sobre clientes.
- **Contracts** — contratos de energia (número, período, montante, preço, status, tipo). Referencia um
  cliente (`client_id`) e o usuário atuante. Publica eventos de contrato no Kafka.
- **Financial** — faturas e pagamentos. Uma fatura referencia um cliente (`client_id`) e nasce de
  contratos. Publica eventos financeiros no Kafka.
- **Audit** — trilha de auditoria **append-only**. **Consumidor de eventos** (RabbitMQ): os
  *registros* chegam pelo barramento (sem upstream síncrono para gravar). Mas a **API REST** do
  audit-service autentica via `auth-service` (`AuthClient` → `/internal/users/by-username`), então
  tem **dependência síncrona de Auth**.
- **Negotiations** (futuro) — negociações e transações de energia sobre contratos.
- **Notifications** (futuro) — notificações a usuários; **consumidor de eventos**.
- **Reports** (futuro) — relatórios; agrega dados de vários contextos (candidato a serviço de
  composição).

---

## 3. Grafo de dependências (acíclico)

A direção das setas é **"depende de / chama"**. O grafo é um **DAG** (sem ciclos), o que garante uma
ordem de extração bem definida e evita dependências circulares entre serviços.

```
                 ┌─────────┐
                 │  Auth   │  (raiz — sem upstream)
                 └────▲────┘
        ┌─────────────┼───────────────┬───────────────┐
        │             │               │               │
   ┌────┴────┐   ┌────┴─────┐    ┌─────┴─────┐   ┌──────┴──────┐
   │ Clients │   │Contracts │    │ Financial │   │Negotiations │
   └────▲────┘   └────▲─────┘    └───────────┘   └─────────────┘
        │             │  ▲              ▲   ▲            ▲
        └─────────────┘  └──────────────┘   │           │
        Contracts→Clients  Financial→Contracts           │
                           Financial→Clients   Negotiations→Contracts

   ┌─────────┐   ┌───────────────┐
   │  Audit  │   │ Notifications │   Audit→Auth (API REST via AuthClient); os REGISTROS chegam por evento.
   └─────────┘   └───────────────┘   Notifications: consumidor de eventos, sem upstream síncrono.
```

**Dependências síncronas (via cliente HTTP), por contexto:**

| Contexto | Depende de (upstream) | Clientes HTTP no serviço |
| :------- | :-------------------- | :----------------------- |
| **Auth** | — (raiz) | nenhum |
| **Clients** | Auth | `AuthClient` |
| **Contracts** | Auth, Clients | `AuthClient`, `ClientClient` |
| **Financial** | Auth, Clients, Contracts | `AuthClient`, `ClientClient`, `ContractClient` |
| **Negotiations** _(futuro)_ | Auth, Contracts | `AuthClient`, `ContractClient` |
| **Audit** | Auth (API REST); registros por evento | `AuthClient` |
| **Notifications** _(futuro)_ | — (consome eventos) | nenhum |
| **Reports** _(futuro)_ | todos (agregação) | vários |

> **Invariante:** um serviço só carrega clientes HTTP para contextos **upstream** dele — nunca para
> downstream. Isso preserva a direção declarada e mantém o grafo acíclico. **Auth** não tem upstream
> síncrono; **Audit** recebe seus registros pelo barramento (RabbitMQ/Kafka) mas depende de **Auth**
> para autenticar a própria API REST (`AuthClient`).

---

## 4. Ordem de extração

Derivada do grafo — **raízes primeiro**, para que cada serviço extraído já dependa de um serviço
_real_ (não de um _stub_), e a primeira extração valide toda a pilha (discovery + HTTP + resiliência):

1. **Auth** (sem upstream) — o _blueprint_; valida Consul + `/health` + Dockerfile ponta a ponta.
2. **Clients** (→ Auth) — introduz o `AuthClient` e a primeira chamada de rede entre serviços.
3. **Contracts** (→ Auth, Clients) — `AuthClient` + `ClientClient`.
4. **Financial** (→ Auth, Clients, Contracts) — `AuthClient` + `ClientClient` + `ContractClient`.
5. **Audit** (→ Auth) — `AuthClient` para autenticar a API REST; os registros de auditoria chegam pelo barramento de eventos.

---

## 5. Regras da decomposição

- **Banco por serviço.** Cada serviço é dono do seu banco/schema e **nunca** lê as tabelas de outro —
  dado que cruza a fronteira do contexto vem pelo **serviço** dono, via cliente HTTP.
- **Comunicação síncrona = HTTP (`httpx`).** As chamadas que antes eram in-process (buscar um usuário,
  buscar um cliente) viram chamadas de rede tipadas por cliente dedicado, preservando a direção.
- **Eventos permanecem eventos.** Audit e Notifications continuam **consumindo** do barramento
  (RabbitMQ/Kafka) — _fire-and-forget_, sem dependência síncrona.
- **Resiliência em toda chamada de rede.** _Timeout_ explícito + _retry_ com _backoff_ (`tenacity`) +
  _fallback_ definido, para que a falha de uma dependência não cascateie pela cadeia da requisição.
- **Descoberta por nome.** Cada serviço se registra no **Consul** (com _health check_ HTTP) e resolve
  dependências pelo **nome lógico**, não por host/porta fixos.
- **Gateway na borda.** O **Traefik** roteia por prefixo de caminho (via catálogo do Consul) e aplica
  autenticação, logging e _rate limiting_ na borda.
</content>
