# ⚡ EnergyHub — Especificação de Requisitos (Fase 0)

Este documento consolida os **requisitos funcionais (RF)** e **não-funcionais (RNF)** da
plataforma **EnergyHub** — o _backend_ de negociação de energia construído com **FastAPI**,
**Clean Architecture** e **DDD**. Ele traduz o escopo do sistema em requisitos verificáveis,
usando exatamente as entidades, enums e _value objects_ definidos no
[modelo canônico da Fase 0](#-referências), fonte única de verdade.

Cada requisito recebe um **ID estável** (`RF-NN` / `RNF-NN`), preservado nas fases seguintes para
rastreabilidade entre casos de uso, modelo de dados, testes e implementação. Os requisitos cobrem
os **9 módulos de negócio** (`auth`, `clients`, `contracts`, `negotiations`, `financial`, `audit`,
`notifications`, `reports` e o transversal `shared`) e as **11 entidades de núcleo**.

> **Convenções de prioridade (RF):** **Alta** = essencial ao MVP da Fase 0 / bloqueia demais
> capacidades · **Média** = necessário ao ciclo completo, mas incremental · **Baixa** = desejável /
> refinamento posterior.

---

## A. Requisitos Funcionais (RF)

### A.1. Cadastro e autenticação de usuários — módulo `auth`

Entidades: `User`, `Role`, `Permission` (junções `user_roles`, `role_permissions`).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-01 | Cadastrar usuário | O **Administrador** cadastra um `User` com `name`, `email` (VO `Email`, único), `password_hash` e `status` inicial `ACTIVE`. Dispara `user.created`. | Alta |
| RF-02 | Autenticar usuário (JWT) | O sistema valida credenciais e emite um **JWT** (HS256) para o `User`; atualiza `last_login_at` e registra ação `LOGIN` na auditoria. | Alta |
| RF-03 | Hash de senha (BCrypt) | Senhas são persistidas apenas como `password_hash` gerado com **BCrypt**; texto plano nunca é armazenado nem logado. | Alta |
| RF-04 | Controle de acesso RBAC | Autorização baseada em papéis: `User` ↔ `Role` (via `user_roles`) e `Role` ↔ `Permission` (via `role_permissions`), avaliando `Permission.code` (ex.: `contracts:create`). | Alta |
| RF-05 | Gerir status do usuário | Suportar `UserStatus` = `ACTIVE` / `INACTIVE` / `BLOCKED`; usuários `INACTIVE`/`BLOCKED` são impedidos de autenticar. | Média |
| RF-06 | Gerir papéis e permissões | O **Administrador** cria, edita e associa `Role` e `Permission`, refletindo em `user_roles` / `role_permissions`. | Média |
| RF-07 | Atualizar/desativar usuário | Atualização de dados (`user.updated`) e desativação lógica via `deleted_at` / `status` (`user.deleted`), com auditoria. | Baixa |

### A.2. Gestão de clientes — módulo `clients`

Entidades: `Client` (raiz do `ClientAggregate`), `Contact` (apoio).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-08 | Cadastrar cliente | O **Operador** cadastra um `Client` com `legal_name`, `cnpj` (VO `CNPJ`, único), `type` e `status` inicial `ACTIVE`. Dispara `client.created`. | Alta |
| RF-09 | Validar CNPJ | O `cnpj` é validado pelo VO `CNPJ` (14 dígitos + dígito verificador); CNPJ inválido ou duplicado é rejeitado. | Alta |
| RF-10 | Diferenciar consumidor/fornecedor | O atributo `type` (`ClientType` = `CONSUMER` / `SUPPLIER`) distingue parte compradora de parte vendedora, reutilizando a mesma entidade `Client`. | Alta |
| RF-11 | Gerir contatos do cliente | Cada `Client` pode ter múltiplos `Contact` (`name`, `email`, `phone`, `type` = `ContactType` `COMMERCIAL`/`FINANCIAL`/`TECHNICAL`). | Média |
| RF-12 | Gerir status do cliente | Suportar `ClientStatus` = `ACTIVE` / `INACTIVE`; clientes `INACTIVE` não podem originar novos contratos. | Média |
| RF-13 | Atualizar dados cadastrais | Atualização de `email` (VO `Email`), `phone` (VO `PhoneNumber`) e endereço (VO `Address`), com auditoria (`client.updated`). | Baixa |

### A.3. Criação de contratos — módulo `contracts`

Entidade: `Contract` (raiz do `ContractAggregate`).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-14 | Criar contrato | O **Operador** cria um `Contract` com `code` (único), `client_id`, `type`, `energy_volume_mwh`, `total_amount` (VO `Money`), `start_date` e `end_date`; nasce em `status` `DRAFT`. Dispara `contract.created`. | Alta |
| RF-15 | Definir tipo do contrato | O `type` (`ContractType` = `PURCHASE` / `SALE`) determina a natureza do contrato (compra ou venda de energia). | Alta |
| RF-16 | Validar período de vigência | Exigir `end_date >= start_date`; períodos inconsistentes são rejeitados na criação/edição. | Alta |
| RF-17 | Registrar volume e valor | Persistir `energy_volume_mwh` (MWh, `NUMERIC(18,4)`) e `total_amount` + `total_amount_currency` (VO `Money`, default `BRL`). | Alta |
| RF-18 | Fluxo de aprovação | Ciclo `DRAFT` → `PENDING_APPROVAL` → `APPROVED` / `REJECTED`, registrando `approved_by` e `approved_at`. Dispara `contract.approved` ou `contract.rejected`. | Alta |
| RF-19 | Ciclo de vida do contrato | Suportar estados adicionais de `ContractStatus`: `ACTIVE`, `EXPIRED`, `CANCELLED`, conforme evolução do contrato. | Média |

### A.4. Registro de negociações — módulo `negotiations`

Entidade: `Negotiation` (raiz do `NegotiationAggregate`).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-20 | Registrar negociação | O **Operador** registra uma `Negotiation` vinculada a um `Contract` (`contract_id`), com `proposed_price` (VO `Money`, preço por MWh), `volume_mwh` e `started_at`. Nasce em `status` `INITIATED`. Dispara `negotiation.initiated`. | Alta |
| RF-21 | Registrar preço proposto | Persistir `proposed_price` + `proposed_price_currency` (default `BRL`) como preço unitário por MWh da proposta. | Alta |
| RF-22 | Evoluir status da negociação | Ciclo `NegotiationStatus`: `INITIATED` → `IN_PROGRESS` → `COMPLETED` / `CANCELLED`, gravando `closed_at` no encerramento. Dispara `negotiation.completed` ou `negotiation.cancelled`. | Alta |
| RF-23 | Vincular à contratação | Toda `Negotiation` referencia obrigatoriamente um `Contract` existente (integridade `contracts.client_id` → contrato → negociação). | Média |

### A.5. Compra de energia — módulo `negotiations` (`EnergyTransaction`)

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-24 | Executar compra de energia | Registrar uma `EnergyTransaction` com `type` = `TransactionType` `BUY`, vinculada a uma `Negotiation` (`negotiation_id`), com `volume_mwh`, `unit_price` (VO `Money`) e `executed_at`. Dispara `energy.bought`. | Alta |
| RF-25 | Calcular total da compra | Calcular e persistir `total_amount = volume_mwh × unit_price` de forma consistente com o VO `Money`. | Alta |

### A.6. Venda de energia — módulo `negotiations` (`EnergyTransaction`)

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-26 | Executar venda de energia | Registrar uma `EnergyTransaction` com `type` = `TransactionType` `SELL`, vinculada a uma `Negotiation`, com `volume_mwh`, `unit_price` e `executed_at`. Dispara `energy.sold`. | Alta |
| RF-27 | Calcular total da venda | Calcular e persistir `total_amount = volume_mwh × unit_price` para a transação de venda. | Alta |

### A.7. Geração de faturas — módulo `financial`

Entidades: `Invoice` (raiz do `FinancialAggregate`), `Payment` (apoio).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-28 | Emitir fatura | Emitir uma `Invoice` com `number` (único), `client_id`, `amount` (VO `Money`), `issue_date` e `due_date`; nasce em `status` `ISSUED`. Pode referenciar `contract_id`. Dispara `invoice.issued`. | Alta |
| RF-29 | Controlar vencimento | Persistir `due_date` e transicionar `InvoiceStatus` para `OVERDUE` quando o vencimento é ultrapassado sem pagamento. | Alta |
| RF-30 | Gerir status da fatura | Suportar `InvoiceStatus` = `ISSUED` / `PAID` / `OVERDUE` / `CANCELLED`, com eventos `invoice.paid` e `invoice.cancelled`. | Alta |
| RF-31 | Registrar pagamento | Registrar `Payment` (`amount`, `method` = `PaymentMethod` `BANK_SLIP`/`PIX`/`TRANSFER`, `paid_at`) e marcar a `Invoice` como `PAID` (`paid_at`). | Média |

### A.8. Auditoria de operações — módulo `audit`

Entidade: `AuditLog` (append-only, imutável).

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-32 | Trilha append-only | Toda operação relevante gera um `AuditLog` **imutável** (somente inserção; sem `UPDATE`/`DELETE`), com `created_at` no momento do fato. | Alta |
| RF-33 | Registrar ator e ação | Cada `AuditLog` grava `user_id` (NULL = ação do **Sistema**), `action` (`AuditAction` = `CREATE`/`UPDATE`/`DELETE`/`LOGIN`/`APPROVE`/`REJECT`/…), `entity_type`, `entity_id`, `payload` (JSONB) e `ip_address`. | Alta |
| RF-34 | Consultar auditoria | O **Administrador/Auditor** consulta a trilha por filtros (usuário, entidade, ação, período), sem poder alterá-la. | Média |

### A.9. Envio de notificações — módulo `notifications`

Entidade: `Notification`.

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-35 | Enviar notificação | Criar e enviar uma `Notification` para um `User` (`user_id`) com `title`, `body` e `channel` = `NotificationChannel` `EMAIL` / `SMS` / `IN_APP`. Dispara `notification.sent`. | Alta |
| RF-36 | Acompanhar status de entrega | Suportar `NotificationStatus` = `PENDING` / `SENT` / `FAILED` / `READ`, gravando `sent_at` e `read_at`. | Média |
| RF-37 | Disparar por eventos de negócio | Notificações são acionadas por eventos (ex.: `contract.approved`, `invoice.issued`, `negotiation.completed`), com o **Sistema** como ator. | Média |

### A.10. Geração de relatórios — módulo `reports`

Entidade: `Report`.

| ID | Requisito | Descrição | Prioridade |
| :--- | :--- | :--- | :---: |
| RF-38 | Gerar relatório | O **Operador/Administrador** solicita um `Report` com `type` = `ReportType` (`SALES`/`PURCHASES`/`FINANCIAL`/`AUDIT`/`CONTRACTS`), `parameters` (JSONB, filtros) e `requested_by`. Dispara `report.generated`. | Alta |
| RF-39 | Selecionar formato de saída | Suportar `format` = `ReportFormat` `PDF` / `CSV` / `XLSX` (default `PDF`), disponibilizando o resultado em `file_url`. | Média |
| RF-40 | Acompanhar geração | Suportar `ReportStatus` = `PENDING` / `GENERATING` / `READY` / `FAILED`, gravando `generated_at` quando concluído. | Média |

---

## B. Requisitos Não-Funcionais (RNF)

| ID | Categoria | Requisito | Meta / Critério de aceitação |
| :--- | :--- | :--- | :--- |
| RNF-01 | Desempenho | Tempo de resposta das APIs REST | **p95 < 200 ms** por requisição sob carga nominal (excluídos jobs assíncronos de relatório/notificação). |
| RNF-02 | Desempenho | Eficiência de consulta | Consultas usam índices e evitam _N+1_; operações de leitura críticas respondem em < 100 ms (p50) com o banco na 3FN. |
| RNF-03 | Escalabilidade | Concorrência de usuários | Suportar **10.000 usuários simultâneos** com escala horizontal (serviços _stateless_, aptos a HPA na Fase 16). |
| RNF-04 | Disponibilidade | _Uptime_ do serviço | **99,9%** de disponibilidade mensal (≈ 43 min de indisponibilidade/mês), com _health checks_ (`/health`) e _readiness/liveness_. |
| RNF-05 | Segurança | Criptografia em trânsito | **TLS 1.2+** obrigatório em todas as comunicações externas; tráfego em texto plano bloqueado. |
| RNF-06 | Segurança | Criptografia em repouso | Dados sensíveis criptografados no armazenamento (volume/disco do PostgreSQL e _backups_). |
| RNF-07 | Segurança | Autenticação | Acesso via **JWT** (HS256) com expiração e renovação controladas; rotas protegidas exigem `Authorization: Bearer`. |
| RNF-08 | Segurança | Autorização (RBAC) | Toda operação sensível é verificada contra `Permission.code`; acesso negado por padrão (_deny by default_). |
| RNF-09 | Segurança | Proteção de senhas | Senhas armazenadas com **BCrypt** (fator de custo ≥ 12); nunca em texto plano, log ou resposta de API. |
| RNF-10 | Conformidade | Regulações do setor elétrico | Aderência às regras do setor (ex.: **CCEE/ANEEL**): rastreabilidade de contratos/transações e retenção de dados regulatórios. |
| RNF-11 | Auditabilidade | Trilha completa | **Toda** operação relevante gera `AuditLog` append-only, cobrindo os atores **Administrador/Operador/Sistema** (ver RF-32/RF-33). |
| RNF-12 | Internacionalização | Suporte a múltiplos idiomas (i18n) | Mensagens e rótulos externalizados; idiomas `pt-BR` (padrão) e `en`; datas/horas em `TIMESTAMPTZ` (UTC) e moeda ISO-4217 (VO `Money`). |
| RNF-13 | Observabilidade | Métricas, logs e alertas | Métricas expostas ao **Prometheus**, logs estruturados e _dashboards_/alertas (Grafana/Alertmanager) a partir da Fase 12. |
| RNF-14 | Manutenibilidade | Qualidade e evolução do código | **Clean Architecture + DDD** com regra de dependência estrita; cobertura de testes ≥ **80%**; `black`/`ruff`/`mypy` no _quality gate_; versionamento SemVer. |
| RNF-15 | Portabilidade | Ambientes reproduzíveis | Execução via **Docker/Docker Compose** e, na Fase 16, **Kubernetes**; configuração por variáveis de ambiente (12-factor). |

> **Rastreabilidade RNF ↔ RF:** RNF-07/08/09 sustentam RF-01…RF-06; RNF-11 sustenta RF-32…RF-34;
> RNF-01/03/04 aplicam-se transversalmente a todos os RF de escrita/leitura.

---

## 📎 Referências

- [01 — Escopo do Sistema](01-escopo-do-sistema.md)
- [03 — Casos de Uso](03-casos-de-uso.md)
- [04 — Modelo de Dados](04-modelo-de-dados.md)
- [07 — Arquitetura](07-arquitetura.md)
