# Fase 0 — Modelagem UML

> Documento de planejamento da **Fase 0** do EnergyHub. Consolida a **modelagem UML** do
> sistema em três vistas complementares: **diagrama de classes** (estrutura do domínio),
> **diagramas de sequência** (comportamento dos principais casos de uso) e **diagrama de
> componentes** (arquitetura em camadas e os 9 módulos). Todos os diagramas seguem o
> **modelo canônico** da Fase 0 (mesmas entidades, VOs, enums, agregados e eventos) e são
> escritos em **Mermaid** — texto versionável, renderizado nativamente pelo GitHub e pela IDE.

Convenções desta modelagem:

- A vista de classes representa o **modelo de domínio** (camada `domain`), portanto usa
  atributos em `camelCase` — diferente do `snake_case` das colunas físicas do banco
  (ver [04-modelo-de-dados.md](./04-modelo-de-dados.md)).
- Estereótipos DDD são aplicados por anotação: `<<AggregateRoot>>` (raiz de agregado),
  `<<Entity>>` (entidade), `<<ValueObject>>` (objeto de valor) e `<<enumeration>>` (enum).
- As **11 entidades de núcleo** são o foco; `Contact` e `Payment` aparecem como entidades de
  apoio dentro de `ClientAggregate` e `FinancialAggregate`.

---

## A. Diagrama de Classes (tarefa 5.1)

O diagrama a seguir descreve as entidades de domínio, seus atributos e **métodos
representativos** (comportamento que expressa as regras de negócio), os **Value Objects**
compartilhados e os relacionamentos com cardinalidade. Os **5 agregados** organizam as
entidades sob uma raiz responsável por manter os invariantes:

| Agregado | Raiz | Membros | Módulo |
| :------- | :--- | :------ | :----- |
| `AuthAggregate` | `User` | `Role`, `Permission` (via `user_roles` / `role_permissions`) | `auth` |
| `ClientAggregate` | `Client` | `Contact` | `clients` |
| `ContractAggregate` | `Contract` | — | `contracts` |
| `NegotiationAggregate` | `Negotiation` | `EnergyTransaction` | `negotiations` |
| `FinancialAggregate` | `Invoice` | `Payment` | `financial` |

As entidades `AuditLog`, `Notification` e `Report` são raízes independentes (fora dos 5
agregados nomeados), cada uma no seu módulo (`audit`, `notifications`, `reports`).

```mermaid
classDiagram
    direction LR

    %% ===================== AuthAggregate =====================
    class User {
        <<AggregateRoot>>
        +UUID id
        +String name
        +Email email
        +String passwordHash
        +UserStatus status
        +DateTime lastLoginAt
        +authenticate(rawPassword) bool
        +assignRole(role) void
        +revokeRole(role) void
        +block() void
        +activate() void
    }
    class Role {
        <<Entity>>
        +UUID id
        +String name
        +String description
        +addPermission(permission) void
        +removePermission(permission) void
        +hasPermission(code) bool
    }
    class Permission {
        <<Entity>>
        +UUID id
        +String code
        +String description
    }

    %% ===================== ClientAggregate =====================
    class Client {
        <<AggregateRoot>>
        +UUID id
        +String legalName
        +String tradeName
        +CNPJ cnpj
        +ClientType type
        +ClientStatus status
        +Email email
        +PhoneNumber phone
        +Address address
        +activate() void
        +deactivate() void
        +addContact(contact) void
        +isSupplier() bool
    }
    class Contact {
        <<Entity>>
        +UUID id
        +UUID clientId
        +String name
        +Email email
        +PhoneNumber phone
        +ContactType type
    }

    %% ===================== ContractAggregate =====================
    class Contract {
        <<AggregateRoot>>
        +UUID id
        +String code
        +UUID clientId
        +ContractType type
        +ContractStatus status
        +Money totalAmount
        +Decimal energyVolumeMwh
        +Date startDate
        +Date endDate
        +UUID approvedBy
        +DateTime approvedAt
        +submitForApproval() void
        +approve(approverId) void
        +reject(approverId, reason) void
        +activate() void
        +expire() void
        +cancel() void
    }

    %% ===================== NegotiationAggregate =====================
    class Negotiation {
        <<AggregateRoot>>
        +UUID id
        +UUID contractId
        +NegotiationStatus status
        +Money proposedPrice
        +Decimal volumeMwh
        +DateTime startedAt
        +DateTime closedAt
        +initiate() void
        +updateProposal(price) void
        +registerPurchase(volume, unitPrice) EnergyTransaction
        +registerSale(volume, unitPrice) EnergyTransaction
        +complete() void
        +cancel() void
    }
    class EnergyTransaction {
        <<Entity>>
        +UUID id
        +UUID negotiationId
        +TransactionType type
        +Decimal volumeMwh
        +Money unitPrice
        +Money totalAmount
        +DateTime executedAt
        +execute() void
        +calculateTotal() Money
    }

    %% ===================== FinancialAggregate =====================
    class Invoice {
        <<AggregateRoot>>
        +UUID id
        +String number
        +UUID clientId
        +UUID contractId
        +InvoiceStatus status
        +Money amount
        +Date issueDate
        +Date dueDate
        +DateTime paidAt
        +issue() void
        +pay(payment) void
        +cancel() void
        +markOverdue() void
        +isOverdue() bool
    }
    class Payment {
        <<Entity>>
        +UUID id
        +UUID invoiceId
        +Money amount
        +PaymentMethod method
        +DateTime paidAt
    }

    %% ===================== Entidades independentes =====================
    class AuditLog {
        <<Entity>>
        +UUID id
        +UUID userId
        +AuditAction action
        +String entityType
        +UUID entityId
        +JSON payload
        +IPAddress ipAddress
        +DateTime createdAt
        +record(userId, action, entityType, entityId) AuditLog
    }
    class Notification {
        <<Entity>>
        +UUID id
        +UUID userId
        +NotificationChannel channel
        +NotificationStatus status
        +String title
        +String body
        +DateTime sentAt
        +DateTime readAt
        +send() void
        +markSent() void
        +markRead() void
        +markFailed() void
    }
    class Report {
        <<Entity>>
        +UUID id
        +ReportType type
        +ReportFormat format
        +ReportStatus status
        +JSON parameters
        +String fileUrl
        +UUID requestedBy
        +DateTime generatedAt
        +generate() void
        +markReady(fileUrl) void
        +markFailed() void
    }

    %% ===================== Value Objects (shared) =====================
    class CNPJ {
        <<ValueObject>>
        +String value
        +isValid() bool
        +formatted() String
    }
    class Email {
        <<ValueObject>>
        +String value
        +isValid() bool
        +domain() String
    }
    class Money {
        <<ValueObject>>
        +Decimal amount
        +String currency
        +add(other) Money
        +multiply(factor) Money
        +isPositive() bool
    }
    class PhoneNumber {
        <<ValueObject>>
        +String value
        +isValid() bool
    }
    class Address {
        <<ValueObject>>
        +String street
        +String number
        +String complement
        +String city
        +String state
        +String zipCode
        +String country
    }
    class Percentage {
        <<ValueObject>>
        +Decimal value
        +apply(amount) Money
    }

    %% ===================== Relacionamentos: agregados / entidades =====================
    User "0..*" -- "0..*" Role : user_roles
    Role "0..*" -- "0..*" Permission : role_permissions
    Client "1" o-- "0..*" Contact : contatos
    Client "1" --> "0..*" Contract : possui
    Contract "0..*" --> "1" User : approvedBy
    Contract "1" --> "0..*" Negotiation : gera
    Negotiation "1" *-- "0..*" EnergyTransaction : transacoes
    Client "1" --> "0..*" Invoice : recebe
    Contract "1" --> "0..*" Invoice : origina
    Invoice "1" o-- "0..*" Payment : pagamentos
    User "1" --> "0..*" AuditLog : registra
    User "1" --> "0..*" Notification : recebe
    User "1" --> "0..*" Report : solicita

    %% ===================== Relacionamentos: Value Objects =====================
    User "1" *-- "1" Email : email
    Client "1" *-- "1" CNPJ : cnpj
    Client "1" *-- "0..1" Email : email
    Client "1" *-- "0..1" PhoneNumber : phone
    Client "1" *-- "0..1" Address : address
    Contract "1" *-- "1" Money : totalAmount
    Negotiation "1" *-- "1" Money : proposedPrice
    EnergyTransaction "1" *-- "1" Money : unitPrice
    Invoice "1" *-- "1" Money : amount
```

> **Sobre `Percentage`:** é um Value Object do módulo `shared` usado nas **regras de
> precificação/reajuste** (ex.: descontos e índices aplicados a `Money`). Não possui
> associação estrutural fixa a uma entidade, por isso aparece como classe independente.
>
> **Enums:** os campos `status`/`type`/`channel`/etc. referenciam as **16 enumerações** do
> modelo canônico. As principais estão detalhadas no diagrama abaixo; a lista completa
> (`UserStatus`, `ClientType`, `ClientStatus`, `ContactType`, `ContractStatus`,
> `ContractType`, `NegotiationStatus`, `TransactionType`, `InvoiceStatus`, `PaymentMethod`,
> `AuditAction`, `NotificationChannel`, `NotificationStatus`, `ReportType`, `ReportFormat`,
> `ReportStatus`) está em [04-modelo-de-dados.md](./04-modelo-de-dados.md).

### A.1 Enumerações principais

```mermaid
classDiagram
    direction LR
    class ContractStatus {
        <<enumeration>>
        DRAFT
        PENDING_APPROVAL
        APPROVED
        ACTIVE
        REJECTED
        EXPIRED
        CANCELLED
    }
    class ContractType {
        <<enumeration>>
        PURCHASE
        SALE
    }
    class NegotiationStatus {
        <<enumeration>>
        INITIATED
        IN_PROGRESS
        COMPLETED
        CANCELLED
    }
    class TransactionType {
        <<enumeration>>
        BUY
        SELL
    }
    class InvoiceStatus {
        <<enumeration>>
        ISSUED
        PAID
        OVERDUE
        CANCELLED
    }
    class UserStatus {
        <<enumeration>>
        ACTIVE
        INACTIVE
        BLOCKED
    }
    class ClientType {
        <<enumeration>>
        CONSUMER
        SUPPLIER
    }
    class NotificationStatus {
        <<enumeration>>
        PENDING
        SENT
        FAILED
        READ
    }
    class ReportStatus {
        <<enumeration>>
        PENDING
        GENERATING
        READY
        FAILED
    }
```

---

## B. Diagramas de Sequência (tarefa 5.2)

Cada diagrama mostra a **interação entre objetos** e o **fluxo de mensagens atravessando as
camadas** — `Router` (Presentation) → `UseCase` (Application) → `Aggregate/Entity` /
`DomainService` (Domain) → `Repository` (interface no domínio, implementação na
infraestrutura) → `PostgreSQL` — além da **emissão de eventos de negócio** pelo
`EventDispatcher`. Os blocos `alt/else` representam os **fluxos alternativos** dos casos de uso.

### B.1 UC-04 — Criar contrato → emite `contract.created`

```mermaid
sequenceDiagram
    autonumber
    actor OP as Operador
    participant R as ContractRouter (Presentation)
    participant UC as CriarContratoUseCase (Application)
    participant AGG as Contract (Domain / ContractAggregate)
    participant REPO as ContractRepository (Domain interface)
    participant PERS as ContractRepositoryImpl (Infrastructure)
    participant DB as PostgreSQL
    participant EV as EventDispatcher (Infrastructure)

    OP->>R: POST /api/v1/contracts (CreateContractRequest)
    R->>UC: execute(CreateContractDTO)
    UC->>REPO: existsByCode(code)
    REPO->>PERS: existsByCode(code)
    PERS->>DB: SELECT 1 FROM contracts WHERE code = code
    DB-->>PERS: vazio
    PERS-->>UC: false
    alt codigo ja existente
        UC-->>R: ContractAlreadyExistsError
        R-->>OP: 409 Conflict
    else codigo disponivel
        UC->>AGG: create(clientId, type, totalAmount, volumeMwh, periodo)
        AGG->>AGG: validar invariantes (endDate >= startDate, volume > 0)
        AGG-->>UC: Contract (status = DRAFT)
        UC->>REPO: save(contract)
        REPO->>PERS: save(contract)
        PERS->>DB: INSERT INTO contracts (...)
        DB-->>PERS: OK
        PERS-->>UC: Contract persistido
        UC->>EV: publish(contract.created)
        EV-->>UC: ack
        UC-->>R: ContractResponseDTO
        R-->>OP: 201 Created
    end
```

### B.2 Aprovar contrato → emite `contract.approved`

Demonstra uma **transição de estado no domínio** (`PENDING_APPROVAL` → `APPROVED`) e a
**distribuição paralela** do evento para os consumidores `financial`, `notifications` e `audit`.

```mermaid
sequenceDiagram
    autonumber
    actor OP as Operador (aprovador)
    participant R as ContractRouter (Presentation)
    participant UC as AprovarContratoUseCase (Application)
    participant REPO as ContractRepository (Domain interface)
    participant PERS as ContractRepositoryImpl (Infrastructure)
    participant CT as Contract (Domain)
    participant DB as PostgreSQL
    participant EV as EventDispatcher
    participant FIN as Modulo financial
    participant NOT as Modulo notifications
    participant AUD as Modulo audit

    OP->>R: POST /api/v1/contracts/:id/approve
    R->>UC: execute(contractId, approverId)
    UC->>REPO: findById(contractId)
    REPO->>PERS: findById(contractId)
    PERS->>DB: SELECT * FROM contracts WHERE id = contractId
    DB-->>PERS: row
    PERS-->>UC: Contract (status = PENDING_APPROVAL)
    alt status invalido para aprovacao
        UC-->>R: InvalidContractStateError
        R-->>OP: 422 Unprocessable Entity
    else transicao valida
        UC->>CT: approve(approverId)
        CT->>CT: validar status == PENDING_APPROVAL
        CT-->>UC: Contract (status = APPROVED, approvedBy, approvedAt)
        UC->>REPO: save(contract)
        REPO->>PERS: save(contract)
        PERS->>DB: UPDATE contracts SET status = APPROVED
        DB-->>PERS: OK
        UC->>EV: publish(contract.approved)
        par consumidor financial
            EV->>FIN: consome contract.approved
        and consumidor notifications
            EV->>NOT: consome contract.approved
        and consumidor audit
            EV->>AUD: consome contract.approved
        end
        UC-->>R: ContractResponseDTO
        R-->>OP: 200 OK
    end
```

### B.3 UC-06 — Comprar energia → cria `EnergyTransaction` → emite `energy.bought`

O caso de compra registra uma `EnergyTransaction` (`type = BUY`) sob a raiz `Negotiation`,
conclui a negociação e publica `energy.bought` para `financial` (gera fatura), `reports`
(atualiza indicadores) e `audit`.

```mermaid
sequenceDiagram
    autonumber
    actor OP as Operador
    participant R as NegotiationRouter (Presentation)
    participant UC as ComprarEnergiaUseCase (Application)
    participant REPO as NegotiationRepository (Domain interface)
    participant PERS as NegotiationRepositoryImpl (Infrastructure)
    participant NEG as Negotiation (Domain / NegotiationAggregate)
    participant TX as EnergyTransaction (Domain)
    participant DB as PostgreSQL
    participant EV as EventDispatcher
    participant FIN as Modulo financial
    participant REP as Modulo reports
    participant AUD as Modulo audit

    OP->>R: POST /api/v1/negotiations/:id/buy (BuyEnergyRequest)
    R->>UC: execute(negotiationId, volumeMwh, unitPrice)
    UC->>REPO: findById(negotiationId)
    REPO->>PERS: findById(negotiationId)
    PERS->>DB: SELECT * FROM negotiations WHERE id = negotiationId
    DB-->>PERS: row
    PERS-->>UC: Negotiation (status = IN_PROGRESS)
    alt negociacao nao esta em andamento
        UC-->>R: InvalidNegotiationStateError
        R-->>OP: 422 Unprocessable Entity
    else negociacao valida
        UC->>NEG: registerPurchase(volumeMwh, unitPrice)
        NEG->>TX: create(type = BUY, volumeMwh, unitPrice)
        TX->>TX: totalAmount = volumeMwh x unitPrice
        TX-->>NEG: EnergyTransaction
        NEG->>NEG: complete() (status = COMPLETED)
        NEG-->>UC: Negotiation + EnergyTransaction
        UC->>REPO: save(negotiation)
        REPO->>PERS: save(negotiation)
        PERS->>DB: INSERT energy_transactions + UPDATE negotiations
        DB-->>PERS: OK
        UC->>EV: publish(energy.bought)
        par consumidor financial
            EV->>FIN: energy.bought (gera fatura)
        and consumidor reports
            EV->>REP: energy.bought (atualiza relatorios)
        and consumidor audit
            EV->>AUD: energy.bought (registra auditoria)
        end
        UC-->>R: EnergyTransactionResponseDTO
        R-->>OP: 201 Created
    end
```

---

## C. Diagrama de Componentes (tarefa 5.3)

### C.1 Vista em camadas (Clean Architecture)

Componentes principais e **interfaces** entre eles. A **regra de dependência** é explícita:
`Presentation → Application → Domain` e `Infrastructure ┄▶ Domain` (a infraestrutura
**implementa** as interfaces do domínio). O **domínio não aponta para nenhuma outra camada**
— ele é o núcleo estável. A apresentação recebe as implementações de infraestrutura por
**injeção de dependência**.

```mermaid
flowchart TB
    subgraph EXT[Clientes e Integracoes]
        HTTP[Cliente HTTP / Swagger UI]
        SYS[Ator Sistema / Jobs]
    end

    subgraph PRES[Presentation]
        direction TB
        RT[Routers FastAPI]
        RQ[Requests / Responses Pydantic]
        EXH[Exception Handlers]
    end

    subgraph APP[Application]
        direction TB
        UCS[Use Cases]
        DTO[DTOs / Mappers]
        ASV[Application Services]
    end

    subgraph DOM[Domain - nucleo estavel]
        direction TB
        ENT[Entities e Aggregates]
        VO[Value Objects]
        RPI[Repository Interfaces]
        EVI[EventPublisher Interface]
        DSV[Domain Services]
    end

    subgraph INFRA[Infrastructure]
        direction TB
        ORM[Persistence SQLAlchemy]
        MSG[Messaging Dispatcher]
        SEC[Security JWT / BCrypt]
        CFG[Config]
    end

    subgraph SVC[Servicos Externos]
        PG[(PostgreSQL 16)]
        RMQ[[RabbitMQ / Kafka]]
        RDS[(Redis)]
    end

    HTTP --> RT
    SYS --> RT
    RT --> UCS
    UCS --> ENT
    UCS --> RPI
    UCS --> EVI
    ORM -. implementa .-> RPI
    MSG -. implementa .-> EVI
    RT -. injecao de dependencia .-> INFRA
    ORM --> PG
    MSG --> RMQ
    SEC --> RDS
```

### C.2 Vista de módulos (9 módulos + `shared` + barramento de eventos)

Todos os módulos de negócio dependem de `shared` (base classes, VOs, contrato de eventos e
exceptions). O acoplamento **entre módulos** é feito por **eventos** através do
`EventDispatcher` — nunca por dependência direta de código, preservando as fronteiras dos
_bounded contexts_.

```mermaid
flowchart TB
    subgraph CORE[Nucleo compartilhado]
        SH["shared - base, VOs, contrato de eventos, exceptions"]
    end

    subgraph MODS[Modulos de negocio]
        AUTH[auth]
        CLI[clients]
        CON[contracts]
        NEG[negotiations]
        FIN[financial]
        AUD[audit]
        NOT[notifications]
        REP[reports]
    end

    BUS{{EventDispatcher / Message Bus}}

    AUTH --> SH
    CLI --> SH
    CON --> SH
    NEG --> SH
    FIN --> SH
    AUD --> SH
    NOT --> SH
    REP --> SH

    AUTH -- user.created --> BUS
    CLI -- client.created --> BUS
    CON -- contract.approved --> BUS
    NEG -- energy.bought / negotiation.completed --> BUS
    FIN -- invoice.issued / invoice.paid --> BUS

    BUS -- consome --> FIN
    BUS -- consome --> NOT
    BUS -- consome --> AUD
    BUS -- consome --> REP
```

**Interfaces entre componentes (contratos):**

| Interface (Domain) | Implementação (Infrastructure) | Consumidor (Application) |
| :----------------- | :----------------------------- | :----------------------- |
| `XxxRepository` (ex.: `ContractRepository`) | `XxxRepositoryImpl` (SQLAlchemy) | Use Cases |
| `EventPublisher` | `EventDispatcher` / adaptador de mensageria | Use Cases |
| `PasswordHasher` | `BCryptHasher` (passlib) | `auth` use cases |
| `TokenProvider` | `JwtTokenProvider` (python-jose) | `auth` use cases |

---

## D. Ferramentas e versionamento dos diagramas (tarefa 5.4)

Todos os diagramas UML desta modelagem — **classes**, **sequência** e **componentes** — são
escritos em **Mermaid**, em blocos ` ```mermaid ` embutidos nesta própria documentação. Essa
escolha traz vantagens de engenharia:

- **Versionáveis em Git:** os diagramas são texto, portanto entram em _diff_, _code review_
  e histórico como qualquer outro artefato do repositório.
- **Renderização nativa:** GitHub, GitLab e as principais IDEs (VS Code, PyCharm) renderizam
  Mermaid sem plugins externos ou binários.
- **Baixo custo de manutenção:** evoluem junto com o código e o modelo canônico, sem
  arquivos binários (`.drawio`, imagens) que desatualizam silenciosamente.

Alternativas como Draw.io permanecem válidas conforme a especificação, mas o padrão do
projeto é **Mermaid como fonte única** dos diagramas na documentação.

---

## Referências

- [03-casos-de-uso.md](./03-casos-de-uso.md) — casos de uso (UC-01 a UC-11) e diagrama de casos de uso.
- [04-modelo-de-dados.md](./04-modelo-de-dados.md) — DER, entidades, atributos, tipos e enums.
- [07-arquitetura.md](./07-arquitetura.md) — Clean Architecture, camadas, módulos e regra de dependência.
