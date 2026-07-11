# ⚡ EnergyHub — Eventos de Negócio (Fase 0)

Este documento cataloga os **eventos de negócio** do EnergyHub — os fatos relevantes que ocorrem
no domínio (um usuário foi criado, um contrato foi aprovado, uma fatura foi paga) e que precisam
ser comunicados de forma **assíncrona** entre os módulos. Ele define, para cada evento, seu
**nome**, **gatilho (trigger)**, **módulo produtor**, **consumidores** e a **estrutura do
payload**. É a fonte para o desacoplamento entre módulos e para a trilha de auditoria, e apoia
diretamente os casos de uso (03), o modelo de dados (04) e a arquitetura (07).

> 📌 Este documento é derivado do **modelo canônico da Fase 0** e usa exatamente os mesmos nomes
> de eventos, entidades, módulos e enums. Em caso de divergência, o modelo canônico prevalece.

---

## 🧭 1. Abordagem orientada a eventos

O EnergyHub adota uma arquitetura **orientada a eventos** (_event-driven_) para comunicar mudanças
de estado entre os **9 módulos** de negócio sem acoplá-los diretamente. Em vez de um módulo chamar
outro de forma síncrona, ele **publica um evento** descrevendo o que aconteceu; os módulos
interessados **consomem** esse evento e reagem de forma independente.

Essa abordagem traz três benefícios centrais para a plataforma:

| Benefício | Descrição |
| :-------- | :-------- |
| **Desacoplamento** | O produtor não conhece seus consumidores. `contracts` emite `contract.approved` sem saber que `financial`, `notifications` e `audit` reagirão. |
| **Auditabilidade** | Praticamente todo evento é consumido pelo módulo `audit`, alimentando a trilha _append-only_ (`AuditLog`) exigida para conformidade (CCEE/ANEEL). |
| **Extensibilidade** | Novos consumidores (busca, cache, relatórios, integrações) podem ser adicionados sem alterar o produtor. |

### 1.1 🚚 Transporte

O transporte dos eventos evolui ao longo do roadmap, mas o **contrato do evento (envelope +
payload) permanece o mesmo**, garantindo que a migração de transporte não quebre produtores nem
consumidores:

| Momento | Transporte | Descrição |
| :------ | :--------- | :-------- |
| **Agora (Fases 0–9)** | **Dispatcher em processo** (_in-process_) | Um despachante síncrono/assíncrono dentro do próprio processo FastAPI entrega o evento aos handlers registrados. Simples, sem infraestrutura externa. |
| **A partir da Fase 10** | **RabbitMQ / Apache Kafka** | Os eventos passam a trafegar por um _broker_ de mensageria (RabbitMQ via `aio-pika`, Kafka via `aiokafka`), habilitando entrega distribuída, _retry_, filas de _dead-letter_ e consumidores em processos/serviços separados. |

> 🧭 Como o **envelope de evento** é estável, o mesmo evento publicado hoje pelo dispatcher em
> processo será, na Fase 10, apenas serializado e publicado em uma _exchange_/tópico — sem
> alterar sua semântica de negócio.

### 1.2 ✉️ Envelope de evento (comum a todos)

Todo evento de negócio é publicado com um **envelope padrão** (definido no módulo `shared`). O
envelope carrega os metadados comuns; o campo `data` carrega o payload específico de cada evento.

| Campo | Tipo | Descrição |
| :---- | :--- | :-------- |
| `event_id` | UUID | Identificador único da ocorrência do evento (idempotência). |
| `event_name` | string | Nome do evento no formato `dominio.acao` (ex.: `contract.approved`). |
| `occurred_at` | string (ISO-8601) | Instante em que o fato ocorreu, em UTC. |
| `version` | inteiro | Versão do esquema do evento (evolução de contrato). |
| `producer` | string | Módulo que publicou o evento (ex.: `contracts`). |
| `data` | objeto | Payload específico do evento — ids das entidades e campos relevantes. |

```json
{
  "event_id": "3f2504e0-4f89-41d3-9a0c-0305e82c3301",
  "event_name": "contract.approved",
  "occurred_at": "2026-07-11T14:00:00Z",
  "version": 1,
  "producer": "contracts",
  "data": {
    "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "approved_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
    "total_amount": { "amount": "150000.00", "currency": "BRL" },
    "energy_volume_mwh": "500.0000",
    "approved_at": "2026-07-11T14:00:00Z"
  }
}
```

> ℹ️ Nas seções de detalhamento, os exemplos mostram **apenas o conteúdo do campo `data`** — o
> envelope é sempre o mesmo e envolve esse payload. Valores monetários seguem o VO `Money`
> (`{ "amount": "<Decimal>", "currency": "<ISO-4217>" }`) e a energia é expressa em **MWh**
> (`NUMERIC(18,4)`, representada como string para preservar a precisão decimal).

---

## 📇 2. Catálogo de eventos

Os **18 eventos de negócio** da Fase 0 seguem a nomenclatura `dominio.acao`. A tabela abaixo
resume produtor, gatilho e consumidores de cada um. Os consumidores usam os módulos `audit`
(trilha), `notifications` (avisos), `financial` (faturamento) e `reports` (relatórios).

| # | Evento | Módulo produtor | Trigger (quando) | Consumidores |
| :-: | :----- | :-------------- | :--------------- | :----------- |
| 1 | `user.created` | `auth` | Usuário cadastrado no sistema | `notifications`, `audit` |
| 2 | `user.updated` | `auth` | Dados do usuário alterados | `audit` |
| 3 | `user.deleted` | `auth` | Usuário removido/desativado | `audit`, `notifications` |
| 4 | `client.created` | `clients` | Cliente/fornecedor cadastrado | `audit`, `notifications` |
| 5 | `client.updated` | `clients` | Cliente alterado | `audit` |
| 6 | `contract.created` | `contracts` | Contrato criado (`DRAFT`) | `audit`, `notifications` |
| 7 | `contract.approved` | `contracts` | Contrato aprovado | `financial`, `notifications`, `audit` |
| 8 | `contract.rejected` | `contracts` | Contrato rejeitado | `notifications`, `audit` |
| 9 | `negotiation.initiated` | `negotiations` | Negociação iniciada | `audit` |
| 10 | `negotiation.completed` | `negotiations` | Negociação concluída | `financial`, `notifications`, `audit` |
| 11 | `negotiation.cancelled` | `negotiations` | Negociação cancelada | `notifications`, `audit` |
| 12 | `energy.bought` | `negotiations` | Transação de compra executada | `financial`, `reports`, `audit` |
| 13 | `energy.sold` | `negotiations` | Transação de venda executada | `financial`, `reports`, `audit` |
| 14 | `invoice.issued` | `financial` | Fatura emitida | `notifications`, `audit` |
| 15 | `invoice.paid` | `financial` | Fatura paga | `notifications`, `reports`, `audit` |
| 16 | `invoice.cancelled` | `financial` | Fatura cancelada | `notifications`, `audit` |
| 17 | `notification.sent` | `notifications` | Notificação enviada | `audit` |
| 18 | `report.generated` | `reports` | Relatório gerado | `notifications`, `audit` |

---

## 🔎 3. Detalhamento por evento

Cada evento é descrito a seguir com **Nome**, **Trigger**, **Produtor**, **Consumidores** e um
exemplo concreto do payload (`data`). Os exemplos usam um elenco fixo de identificadores para
contar uma **história coerente**: a operadora Ana cadastra o cliente _Indústria Solar_, cria e
aprova o contrato `CT-2026-000123`, que dá origem a uma negociação, transações de energia, uma
fatura e as notificações e relatórios correspondentes.

### 👤 3.1 Usuário (`auth`)

#### 6.1 `user.created`

- **Trigger:** um novo usuário (`User`) é cadastrado com sucesso (UC-01).
- **Produtor:** `auth`
- **Consumidores:** `notifications` (envia boas-vindas / credenciais), `audit` (registra `CREATE`)

```json
{
  "user_id": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "name": "Ana Ribeiro",
  "email": "ana.ribeiro@energyhub.com.br",
  "status": "ACTIVE",
  "roles": ["OPERADOR"],
  "created_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
  "created_at": "2026-07-11T13:30:00Z"
}
```

#### 6.2 `user.updated`

- **Trigger:** dados de um usuário existente são alterados (nome, status, papéis, etc.).
- **Produtor:** `auth`
- **Consumidores:** `audit` (registra `UPDATE` com o diff)

```json
{
  "user_id": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "changed_fields": {
    "name": { "old": "Ana Ribeiro", "new": "Ana R. Ribeiro" },
    "status": { "old": "ACTIVE", "new": "INACTIVE" }
  },
  "updated_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
  "updated_at": "2026-07-11T15:10:00Z"
}
```

#### 6.3 `user.deleted`

- **Trigger:** um usuário é removido ou desativado (soft-delete via `deleted_at`).
- **Produtor:** `auth`
- **Consumidores:** `audit` (registra `DELETE`), `notifications` (avisa o usuário/administrador)

```json
{
  "user_id": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "email": "ana.ribeiro@energyhub.com.br",
  "soft_delete": true,
  "reason": "Desligamento do colaborador.",
  "deleted_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
  "deleted_at": "2026-07-11T16:00:00Z"
}
```

### 🏢 3.2 Cliente (`clients`)

#### 6.4 `client.created`

- **Trigger:** um cliente ou fornecedor (`Client`) é cadastrado (UC-03).
- **Produtor:** `clients`
- **Consumidores:** `audit` (registra `CREATE`), `notifications` (confirma cadastro)

```json
{
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "legal_name": "Indústria Solar Ltda",
  "trade_name": "SolarInd",
  "cnpj": "12345678000199",
  "type": "CONSUMER",
  "status": "ACTIVE",
  "email": "contato@solarind.com.br",
  "created_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "created_at": "2026-07-11T13:45:00Z"
}
```

#### 6.5 `client.updated`

- **Trigger:** dados cadastrais de um cliente são alterados (status, contato, endereço, etc.).
- **Produtor:** `clients`
- **Consumidores:** `audit` (registra `UPDATE` com o diff)

```json
{
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "changed_fields": {
    "status": { "old": "ACTIVE", "new": "INACTIVE" },
    "email": { "old": "contato@solarind.com.br", "new": "financeiro@solarind.com.br" }
  },
  "updated_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "updated_at": "2026-07-11T15:20:00Z"
}
```

### 📄 3.3 Contrato (`contracts`)

#### 6.6 `contract.created`

- **Trigger:** um contrato (`Contract`) é criado no estado `DRAFT` (UC-04).
- **Produtor:** `contracts`
- **Consumidores:** `audit` (registra `CREATE`), `notifications` (avisa responsáveis)

```json
{
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "code": "CT-2026-000123",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "type": "PURCHASE",
  "status": "DRAFT",
  "total_amount": { "amount": "150000.00", "currency": "BRL" },
  "energy_volume_mwh": "500.0000",
  "start_date": "2026-08-01",
  "end_date": "2027-07-31",
  "created_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "created_at": "2026-07-11T13:50:00Z"
}
```

#### 6.7 `contract.approved`

- **Trigger:** um contrato em `PENDING_APPROVAL` é aprovado, indo para `APPROVED`.
- **Produtor:** `contracts`
- **Consumidores:** `financial` (habilita faturamento), `notifications` (avisa cliente/operador), `audit` (registra `APPROVE`)

```json
{
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "approved_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
  "total_amount": { "amount": "150000.00", "currency": "BRL" },
  "energy_volume_mwh": "500.0000",
  "approved_at": "2026-07-11T14:00:00Z"
}
```

#### 6.8 `contract.rejected`

- **Trigger:** um contrato em `PENDING_APPROVAL` é rejeitado, indo para `REJECTED`.
- **Produtor:** `contracts`
- **Consumidores:** `notifications` (avisa o criador com o motivo), `audit` (registra `REJECT`)

```json
{
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "rejected_by": "2b7e1516-28ae-4f3c-9b2a-1c9f0d4a5e6b",
  "reason": "Volume acima do limite de crédito aprovado para o cliente.",
  "rejected_at": "2026-07-11T14:05:00Z"
}
```

### 🤝 3.4 Negociação (`negotiations`)

#### 6.9 `negotiation.initiated`

- **Trigger:** uma negociação (`Negotiation`) é iniciada (`INITIATED`) para um contrato (UC-05).
- **Produtor:** `negotiations`
- **Consumidores:** `audit` (registra `CREATE`)

```json
{
  "negotiation_id": "a1c0ffee-1234-4567-89ab-cdef01234567",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "INITIATED",
  "proposed_price": { "amount": "300.00", "currency": "BRL" },
  "volume_mwh": "500.0000",
  "started_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "started_at": "2026-07-11T14:10:00Z"
}
```

#### 6.10 `negotiation.completed`

- **Trigger:** uma negociação é concluída com acordo (`COMPLETED`), registrando `closed_at`.
- **Produtor:** `negotiations`
- **Consumidores:** `financial` (base para faturamento), `notifications` (avisa as partes), `audit` (registra `UPDATE`)

```json
{
  "negotiation_id": "a1c0ffee-1234-4567-89ab-cdef01234567",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "COMPLETED",
  "final_price": { "amount": "295.00", "currency": "BRL" },
  "volume_mwh": "500.0000",
  "total_amount": { "amount": "147500.00", "currency": "BRL" },
  "closed_at": "2026-07-11T14:30:00Z"
}
```

#### 6.11 `negotiation.cancelled`

- **Trigger:** uma negociação é cancelada antes da conclusão (`CANCELLED`).
- **Produtor:** `negotiations`
- **Consumidores:** `notifications` (avisa as partes), `audit` (registra `UPDATE`)

```json
{
  "negotiation_id": "a1c0ffee-1234-4567-89ab-cdef01234567",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "CANCELLED",
  "reason": "Cliente desistiu antes do fechamento do preço.",
  "cancelled_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "closed_at": "2026-07-11T14:35:00Z"
}
```

### ⚡ 3.5 Energia (`negotiations`)

> As transações de energia (`EnergyTransaction`) pertencem ao agregado `NegotiationAggregate`,
> portanto os eventos `energy.bought` / `energy.sold` são publicados pelo módulo `negotiations`.

#### 6.12 `energy.bought`

- **Trigger:** uma transação de **compra** (`EnergyTransaction` com `type = BUY`) é executada (UC-06).
- **Produtor:** `negotiations`
- **Consumidores:** `financial` (gera fatura), `reports` (agrega volume/valor de compras), `audit` (registra `CREATE`)

```json
{
  "transaction_id": "c4f0e2d1-9a8b-4c3d-8e7f-6a5b4c3d2e1f",
  "negotiation_id": "a1c0ffee-1234-4567-89ab-cdef01234567",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "type": "BUY",
  "volume_mwh": "500.0000",
  "unit_price": { "amount": "295.00", "currency": "BRL" },
  "total_amount": { "amount": "147500.00", "currency": "BRL" },
  "executed_at": "2026-07-11T14:40:00Z"
}
```

#### 6.13 `energy.sold`

- **Trigger:** uma transação de **venda** (`EnergyTransaction` com `type = SELL`) é executada (UC-07).
- **Produtor:** `negotiations`
- **Consumidores:** `financial` (gera fatura), `reports` (agrega volume/valor de vendas), `audit` (registra `CREATE`)

```json
{
  "transaction_id": "d5b1c9a0-6f7e-4a2b-9c8d-1e2f3a4b5c6d",
  "negotiation_id": "a1c0ffee-1234-4567-89ab-cdef01234567",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "type": "SELL",
  "volume_mwh": "250.0000",
  "unit_price": { "amount": "310.00", "currency": "BRL" },
  "total_amount": { "amount": "77500.00", "currency": "BRL" },
  "executed_at": "2026-07-11T14:45:00Z"
}
```

### 💰 3.6 Fatura (`financial`)

#### 6.14 `invoice.issued`

- **Trigger:** uma fatura (`Invoice`) é emitida (`ISSUED`) para um cliente (UC-08).
- **Produtor:** `financial`
- **Consumidores:** `notifications` (envia a fatura/aviso de vencimento), `audit` (registra `CREATE`)

```json
{
  "invoice_id": "e5d4c3b2-a1f0-4e9d-8c7b-6a5f4e3d2c1b",
  "number": "NF-2026-000456",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "contract_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "ISSUED",
  "amount": { "amount": "147500.00", "currency": "BRL" },
  "issue_date": "2026-07-11",
  "due_date": "2026-08-10",
  "issued_at": "2026-07-11T14:50:00Z"
}
```

#### 6.15 `invoice.paid`

- **Trigger:** uma fatura é quitada, indo para `PAID` e registrando `paid_at` e o `Payment`.
- **Produtor:** `financial`
- **Consumidores:** `notifications` (confirma o pagamento), `reports` (atualiza recebíveis), `audit` (registra `UPDATE`)

```json
{
  "invoice_id": "e5d4c3b2-a1f0-4e9d-8c7b-6a5f4e3d2c1b",
  "number": "NF-2026-000456",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "status": "PAID",
  "amount": { "amount": "147500.00", "currency": "BRL" },
  "payment_method": "PIX",
  "paid_at": "2026-07-20T09:15:00Z"
}
```

#### 6.16 `invoice.cancelled`

- **Trigger:** uma fatura `ISSUED` ou `OVERDUE` é cancelada (`CANCELLED`).
- **Produtor:** `financial`
- **Consumidores:** `notifications` (avisa o cliente), `audit` (registra `UPDATE`)

```json
{
  "invoice_id": "e5d4c3b2-a1f0-4e9d-8c7b-6a5f4e3d2c1b",
  "number": "NF-2026-000456",
  "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "status": "CANCELLED",
  "reason": "Emissão em duplicidade; será reemitida com o valor correto.",
  "cancelled_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "cancelled_at": "2026-07-12T10:00:00Z"
}
```

### 🔔 3.7 Notificação (`notifications`)

#### 6.17 `notification.sent`

- **Trigger:** uma notificação (`Notification`) é entregue com sucesso, indo para `SENT` (UC-10).
- **Produtor:** `notifications`
- **Consumidores:** `audit` (registra `CREATE`/entrega)

```json
{
  "notification_id": "1a2b3c4d-5e6f-4071-8293-a4b5c6d7e8f9",
  "user_id": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "channel": "EMAIL",
  "status": "SENT",
  "title": "Contrato CT-2026-000123 aprovado",
  "sent_at": "2026-07-11T14:01:00Z"
}
```

### 📊 3.8 Relatório (`reports`)

#### 6.18 `report.generated`

- **Trigger:** um relatório (`Report`) termina de ser gerado, indo para `READY` (UC-11).
- **Produtor:** `reports`
- **Consumidores:** `notifications` (avisa que o arquivo está pronto), `audit` (registra `CREATE`)

```json
{
  "report_id": "f0e1d2c3-b4a5-4697-8879-0a1b2c3d4e5f",
  "type": "FINANCIAL",
  "format": "PDF",
  "status": "READY",
  "parameters": {
    "period_start": "2026-07-01",
    "period_end": "2026-07-31",
    "client_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  },
  "file_url": "https://storage.energyhub/reports/financial-2026-07.pdf",
  "requested_by": "8f14e45f-ceea-467a-9575-1c1a8c5e2f10",
  "generated_at": "2026-07-11T15:00:00Z"
}
```

---

## 📚 Referências

Documentos irmãos da Fase 0 (planejamento e design do sistema):

- [03 — Casos de Uso](03-casos-de-uso.md)
- [04 — Modelo de Dados](04-modelo-de-dados.md)
- [07 — Arquitetura](07-arquitetura.md)
