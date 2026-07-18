# ⚡ EnergyHub — Arquitetura Base (as-built · Fases 2–17)

Este documento descreve a arquitetura **como construída** (_as-built_) do EnergyHub ao final das
**Fases 2 a 17 — Clean Architecture, Classes Base, Modelo de Domínio (DDD), Schema do Banco,
Persistência, API REST, Segurança (JWT/RBAC), Documentação/Erros da API, Cache Redis, Mensageria
(RabbitMQ & Kafka), Busca (Elasticsearch), Observabilidade (Prometheus/Grafana), a Suíte de Testes
com _quality gate_ de cobertura, a Containerização (Docker/Compose), a Decomposição em
Microsserviços (Consul/Traefik), a Orquestração com Kubernetes (§21) e a Automação CI/CD (§22)** —
marco `1.0.0`, mais o ciclo de endurecimento pós-`1.0.0` (Kustomize/KRaft/PVCs, guarda de produção,
TLS, NetworkPolicies e supply-chain do CI/CD). Enquanto o [documento de arquitetura da Fase 0](./fase-0/07-arquitetura.md)
define _como o código **deveria** se organizar_ (arquitetura planejada), este artefato registra _o que
**de fato** existe no repositório_: o esqueleto completo de **9 módulos × 4 camadas**, as
**classes-base** já implementadas em `shared`, o **modelo de domínio** (entidades, _value objects_,
enums e agregados) das Fases 2–3, o **schema PostgreSQL + migrações Alembic** da Fase 4, a **camada de
persistência** (ORM async + repositórios) da Fase 5, a **API REST** (DTOs, serviços, use cases e
routers) da Fase 6, a **camada de segurança** (login JWT, `get_current_user`, RBAC por permissão) da
Fase 7, a **documentação da API** (OpenAPI curado + erros padronizados) da Fase 8, o **cache Redis**
(fastapi-cache2 + invalidação) da Fase 9, a **camada de mensageria assíncrona** (produtores/consumidores
RabbitMQ + Kafka) da Fase 10, o **subsistema de busca** (Elasticsearch + full-text/filtros) da Fase 11,
a **camada de observabilidade** (métricas Prometheus + Grafana/Alertmanager) da Fase 12, a **suíte de
testes automatizados** (unitários + componente + integração, com gate de 80% de cobertura) da Fase 13,
a **containerização e orquestração** (Dockerfile multi-stage + Docker Compose) da Fase 14,
a **decomposição em microsserviços** (5 serviços + Consul + clientes HTTP resilientes + gateway Traefik)
da Fase 15, suas **assinaturas reais** e como estendê-las nas próximas fases.

> 📌 Tudo o que segue foi verificado lendo o código-fonte real em `energyhub/src/energyhub/`.
> Em caso de divergência entre a arquitetura planejada (Fase 0) e o código, **este documento**
> reflete o estado atual do repositório; a Fase 0 permanece como a intenção de design.

---

## 🏛️ 1. Visão geral

O EnergyHub segue **Clean Architecture** e **Domain-Driven Design (DDD)** sobre a stack
**Python 3.12+ · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16**. Ao final da Fase 7, o código
Python está organizado assim:

| Dimensão | Valor (as-built) |
| :------- | :--------------- |
| **Layout** | `src` layout — o pacote vive em `energyhub/src/energyhub/` (não é _flat_) |
| **Módulos** | **9**: `shared`, `auth`, `clients`, `contracts`, `negotiations`, `financial`, `audit`, `notifications`, `reports` |
| **Camadas por módulo** | **4**: `domain`, `application`, `infrastructure`, `presentation` |
| **Classes-base** | Concentradas em `shared`, uma para cada bloco fundamental das 4 camadas |
| **App FastAPI** | `src/energyhub/main.py` — `/`, `/health`, login público `/api/v1/auth/login` e **10 routers** REST protegidos (`/api/v1/…`, 25 endpoints, **54 operações com JWT/RBAC**), CORS, handlers de exceção (domínio→HTTP + 401), `/docs`·`/redoc` |
| **Configuração** | `config/` é **pacote** (não módulo único): `settings.py` + `dependencies/` |

O `shared` é o único módulo **transversal**: não modela negócio, apenas fornece os blocos
reutilizados por todos os demais. Os outros 8 módulos são de **negócio** e, a partir da Fase 3, têm
a camada `domain` preenchida com **entidades, enums e agregados** (ver Seção 8); na Fase 5, a
`infrastructure/persistence` de cada módulo ganhou seu **repositório** (ver Seção 10); na Fase 6, as
camadas `application` (DTOs, mappers, services, use cases) e `presentation` (routers) foram
preenchidas (ver Seção 11); na Fase 7, a `infrastructure/security` e os _guards_ RBAC passaram a
**proteger** esses routers (ver Seção 12). As **4 camadas** estão agora ativas nos módulos de negócio.

> 🧱 A anatomia interna é idêntica em todos os módulos: cada um repete as mesmas **4 camadas** e os
> mesmos **sub-pacotes**. Na Fase 3 a camada `domain` passou a conter código; na Fase 5 a
> `infrastructure/persistence` recebeu os repositórios/filtros; na Fase 6 `application` e
> `presentation` receberam DTOs/mappers/services/use-cases e routers REST.

---

## 🗂️ 2. Estrutura de diretórios

Árvore real do pacote (com o `shared` **expandido** e o módulo `auth` como **exemplo** da anatomia
que se repete nos 8 módulos de negócio):

```text
energyhub/                              # projeto Poetry (raiz Python)
├── pyproject.toml   poetry.lock   README.md
├── .env                                # git-ignored (roda a partir de energyhub/)
├── alembic.ini                         # config do Alembic (Fase 4)
├── alembic/                            # env.py (async · online/offline) · versions/ (9 migrações 0001→0009)
├── src/energyhub/
│   ├── py.typed                        # marcador PEP 561 (pacote tipado) — Fase 4
│   ├── main.py                         # app FastAPI (/ , /health, CORS, login público + routers protegidos)
│   ├── config/                         # pacote de configuração
│   │   ├── __init__.py                 # reexporta Settings, get_settings, settings
│   │   ├── settings.py                 # Settings (pydantic-settings) + get_settings()
│   │   └── dependencies/               # injeção de dependência (vazio até fases futuras)
│   │       └── __init__.py
│   ├── shared/                         # módulo transversal (classes-base)
│   │   ├── domain/
│   │   │   ├── entity/base_entity.py           # BaseEntity
│   │   │   ├── valueobject/                     # 6 VOs (CNPJ, Email, Money, PhoneNumber, Address, Percentage) — Fase 3
│   │   │   ├── repository/repository.py         # Repository[T, ID]
│   │   │   ├── service/                         # (serviços de domínio — futuro)
│   │   │   └── exception/
│   │   │       ├── domain_exception.py          # DomainException
│   │   │       ├── resource_not_found_exception.py
│   │   │       ├── validation_exception.py
│   │   │       └── business_rule_exception.py
│   │   ├── application/
│   │   │   ├── dto/base_dto.py                  # BaseDTO
│   │   │   ├── mapper/                          # (mappers — futuro)
│   │   │   ├── usecase/usecase.py               # UseCase[Input, Output]
│   │   │   ├── service/                         # (serviços de aplicação — futuro)
│   │   │   └── exception/application_exception.py  # ApplicationException
│   │   ├── infrastructure/
│   │   │   ├── persistence/
│   │   │   │   ├── database.py                  # Base declarativa (Fase 4) — target_metadata do Alembic
│   │   │   │   └── sqlalchemy_repository.py     # SQLAlchemyRepository[T, ID]
│   │   │   ├── messaging/                       # (eventos/mensageria — futuro)
│   │   │   ├── config/                          # (config de infra — futuro)
│   │   │   └── security/                        # password_hasher.py · authorization.py (require_permission/role) — Fases 6–7
│   │   ├── presentation/
│   │   │   ├── router/base_router.py            # BaseRouter
│   │   │   ├── request/                         # (schemas de request — futuro)
│   │   │   ├── response/error_response.py       # ErrorResponse
│   │   │   └── exception/global_exception_handler.py  # global_exception_handler
│   │   ├── util/                                # date_utils, string_utils, validation_utils
│   │   ├── constant/                            # application_/cache_/message_constants
│   │   └── enums/                               # (enums transversais — futuro)
│   │
│   ├── auth/                           # ── módulo de negócio (exemplo) ──
│   │   ├── domain/         entity/ valueobject/ repository/ service/ exception/  # domain preenchido na Fase 3: User/Role/Permission + auth_aggregate.py
│   │   ├── application/    dto/ mapper/ usecase/ service/ exception/
│   │   ├── infrastructure/ persistence/ messaging/ config/ security/
│   │   └── presentation/   router/ request/ response/ exception/
│   │
│   ├── clients/  contracts/  negotiations/  financial/           # mesma anatomia de auth/
│   └── audit/    notifications/  reports/                        # mesma anatomia de auth/
│
└── tests/                             # conftest.py (fixture TestClient), test_base_entity.py
```

> ℹ️ Cada pacote e sub-pacote contém um `__init__.py`. Na Fase 3, `shared/domain/valueobject/` e a
> camada `domain/` de cada módulo de negócio (`entity/`, `exception/` e os `*_aggregate.py`) deixaram
> de ser pacotes vazios (ver Seção 8). Os demais diretórios sem arquivo
> `.py` de conteúdo (ex.: `mapper/`, `messaging/`, `service/`) seguem como pacotes vazios, prontos para
> serem preenchidos nas fases seguintes. Na Fase 4, `shared/infrastructure/persistence/` ganhou a
> `Base` declarativa (`database.py`) e o projeto Poetry passou a conter `alembic.ini` + `alembic/`
> (ver Seção 9). O `docker-compose.yml` (PostgreSQL 16) vive na raiz do repositório, um nível acima
> de `energyhub/`.

---

## 🧱 3. Camadas e sub-pacotes

Cada módulo repete as **4 camadas** abaixo, e cada camada tem os mesmos sub-pacotes de
responsabilidade única:

| Camada | Sub-pacotes | Responsabilidade |
| :----- | :---------- | :--------------- |
| 💎 **domain** | `entity/` · `valueobject/` · `repository/` · `service/` · `exception/` | Regras de negócio puras: entidades, _value objects_, **interfaces** de repositório (portas), serviços de domínio e exceções de negócio. Não conhece frameworks. |
| 🧠 **application** | `dto/` · `mapper/` · `usecase/` · `service/` · `exception/` | Orquestração de casos de uso: DTOs de entrada/saída, mapeadores entre DTO e entidade, casos de uso, serviços de aplicação e exceções de aplicação. |
| 🔌 **infrastructure** | `persistence/` · `messaging/` · `config/` · `security/` | Detalhes técnicos e I/O: implementações concretas de repositório (SQLAlchemy), mensageria/eventos, configuração de infra e segurança. **Implementa** as interfaces do `domain`. |
| 🖥️ **presentation** | `router/` · `request/` · `response/` · `exception/` | Interface HTTP (REST): routers FastAPI, _schemas_ de request/response e _handlers_ de exceção que traduzem erros para respostas HTTP. |

---

## 🧩 4. Classes-base compartilhadas (`shared`)

Todas as classes-base já implementadas na Fase 2 vivem em `shared`, uma por bloco fundamental de
cada camada. Caminhos relativos a `src/energyhub/`.

| Classe / função | Arquivo | Propósito | Assinatura-chave |
| :-------------- | :------ | :-------- | :--------------- |
| `BaseEntity` | `shared/domain/entity/base_entity.py` | Raiz comum de toda entidade: identidade + timestamps de auditoria | `@dataclass(kw_only=True)`; `id: UUID`, `created_at: datetime`, `updated_at: datetime`; `__post_init__()`; `update_timestamp()` |
| `Repository[T, ID]` | `shared/domain/repository/repository.py` | Porta de persistência genérica (contrato CRUD, sem infra) | `ABC`, `async save/find_by_id/find_all/delete_by_id/exists_by_id` |
| `DomainException` | `shared/domain/exception/domain_exception.py` | Raiz da hierarquia de erros de negócio | `__init__(message: str)`; expõe `.message`; `__str__` |
| `ResourceNotFoundException` | `shared/domain/exception/resource_not_found_exception.py` | Recurso solicitado não existe | `class ...(DomainException)` |
| `ValidationException` | `shared/domain/exception/validation_exception.py` | Dados violam regras de validação do domínio | `class ...(DomainException)` |
| `BusinessRuleException` | `shared/domain/exception/business_rule_exception.py` | Regra de negócio violada | `class ...(DomainException)` |
| `BaseDTO` | `shared/application/dto/base_dto.py` | Campos comuns (opcionais) de transporte para DTOs | `@dataclass`; `id/created_at/updated_at` opcionais (`None`) |
| `UseCase[Input, Output]` | `shared/application/usecase/usecase.py` | Contrato de caso de uso | `ABC`, `async execute(input_data: Input) -> Output` |
| `ApplicationException` | `shared/application/exception/application_exception.py` | Erro da camada de aplicação (orquestração) | `__init__(message: str)`; expõe `.message`; `__str__` |
| `SQLAlchemyRepository[T, ID]` | `shared/infrastructure/persistence/sqlalchemy_repository.py` | Implementação CRUD assíncrona de `Repository` (Fase 5) | `__init__(session: AsyncSession, entity_type: type[T])`; `save` faz `flush` (não `commit`); + `find_by`/`find_page` |
| `BaseRouter` | `shared/presentation/router/base_router.py` | Encapsula `APIRouter` padronizando prefixo/tags/dependências | `__init__(prefix="", tags=None, dependencies=None)` — `dependencies` habilita proteção de grupo (Fase 7); `get_router() -> APIRouter` |
| `global_exception_handler` | `shared/presentation/exception/global_exception_handler.py` | Converte qualquer exceção não tratada em resposta 500 padronizada | `async (request: Request, exc: Exception) -> JSONResponse` |
| `ErrorResponse` | `shared/presentation/response/error_response.py` | Corpo padronizado de erro da API | `@dataclass`; `timestamp: str`, `status: int`, `error: str`, `message: str`, `path: str` |

### 4.1 💎 `BaseEntity` — por que `kw_only=True`

`BaseEntity` é declarada com `@dataclass(kw_only=True)`. Isso é **essencial**: os campos herdados
(`id`, `created_at`, `updated_at`) têm _default_, então uma subclasse que declare um campo
**obrigatório** (sem _default_) quebraria a regra "campos sem default não podem vir depois de
campos com default" de um dataclass posicional. Sendo _keyword-only_, a ordenação deixa de
importar. Exemplo de subclasse com campo obrigatório:

```python
from dataclasses import dataclass
from energyhub.shared.domain.entity.base_entity import BaseEntity


@dataclass(kw_only=True)
class Client(BaseEntity):
    name: str                 # obrigatório — só é possível graças a kw_only=True
    cnpj: str

c = Client(name="Usina X", cnpj="12345678000199")   # id/created_at/updated_at são gerados
c.update_timestamp()                                  # ao mutar, atualize updated_at
```

### 4.2 🔌 Implementando um `Repository` concreto

O `domain` declara a **porta** (`Repository[T, ID]`); a `infrastructure` fornece o **adaptador**.
`SQLAlchemyRepository` já implementa todo o CRUD assíncrono; um repositório de módulo normalmente
apenas o especializa:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from energyhub.shared.infrastructure.persistence.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

class SqlAlchemyClientRepository(SQLAlchemyRepository[ClientModel, UUID]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ClientModel)
    # herda save / find_by_id / find_all / delete_by_id / exists_by_id (todos async)
```

> ⚠️ `SQLAlchemyRepository` recebe o `entity_type` e assume que a entidade mapeada possui coluna
> `id`. Na Fase 5, o mapeamento é **imperativo** (ver Seção 10): a entidade continua uma _dataclass_
> pura e o mapper a instrumenta em runtime — por isso o mypy não enxerga as colunas nas queries, e há
> um _override_ de mypy escopado a `*.infrastructure.persistence.*`.

### 4.3 🧠 Criando um `UseCase`

Um caso de uso implementa o contrato `UseCase[Input, Output]` com um único método `async execute`:

```python
from dataclasses import dataclass
from energyhub.shared.application.usecase.usecase import UseCase


@dataclass
class CreateClientInput:
    name: str
    cnpj: str


class CreateClientUseCase(UseCase[CreateClientInput, ClientDTO]):
    def __init__(self, repository: ClientRepository) -> None:
        self._repository = repository

    async def execute(self, input_data: CreateClientInput) -> ClientDTO:
        entity = Client(name=input_data.name, cnpj=input_data.cnpj)
        saved = await self._repository.save(entity)
        return ClientMapper.to_dto(saved)
```

---

## 🧭 5. Regra de dependência

A Clean Architecture é preservada por uma **regra de dependência** estrita: o código só aponta
**para dentro**, em direção ao `domain`. A tabela abaixo resume o que cada camada **pode** e
**não pode** importar (verificado no código da Fase 2):

| Camada | ✅ Pode depender de | 🚫 Não pode depender de |
| :----- | :------------------ | :---------------------- |
| 💎 **domain** | Apenas biblioteca-padrão Python e outros elementos do próprio `domain` | `application`, `infrastructure`, `presentation` **e frameworks** (FastAPI, SQLAlchemy, Pydantic) |
| 🧠 **application** | `domain` | `infrastructure`, `presentation` |
| 🔌 **infrastructure** | `domain` (implementa suas interfaces/portas) | `presentation` |
| 🖥️ **presentation** | `application` (e injeta `infrastructure` na composição) | — (é a camada mais externa) |

> 🔒 Na prática: `BaseEntity`, `Repository`, `DomainException` e as 3 subclasses **não importam**
> nenhum framework — só `dataclasses`, `datetime`, `uuid`, `abc`, `typing`. Já
> `SQLAlchemyRepository` (infra) importa SQLAlchemy e `global_exception_handler`/`BaseRouter`
> (presentation) importam FastAPI. Na Fase 3, todo o domínio de negócio (entidades, VOs, enums,
> agregados e exceções) também depende apenas da biblioteca-padrão — **zero imports de framework**.
> Verificação (Fases 2–3): **268 módulos importam sem erro**; `ruff` / `mypy` (269 arquivos) /
> `black` limpos; smoke test comportamental do domínio (VOs, validações, regras do `Contract`,
> agregados) verde.

---

## 🧰 6. `shared/util`, `shared/constant`, `shared/enums`

Blocos utilitários transversais já preenchidos (exceto `enums`, ainda vazio):

### 6.1 `shared/util/` — funções auxiliares puras

| Arquivo | Funções | Observação |
| :------ | :------ | :--------- |
| `date_utils.py` | `utcnow()`, `to_iso(value)`, `is_past(value)` | Sempre UTC _timezone-aware_ |
| `string_utils.py` | `is_blank(value)`, `normalize_whitespace(value)`, `only_digits(value)` | `only_digits` útil para CNPJ/telefone |
| `validation_utils.py` | `is_valid_email(value)`, `is_valid_cnpj_length(value)`, `is_positive(value)` | Validações básicas — a validação rica (ex.: DV do CNPJ) já vive nos _Value Objects_ (Fase 3, Seção 8) |

### 6.2 `shared/constant/` — constantes nomeadas

| Arquivo | Constantes |
| :------ | :--------- |
| `application_constants.py` | `APP_NAME`, `API_V1_PREFIX` (`/api/v1`), `DEFAULT_PAGE_SIZE` (20), `MAX_PAGE_SIZE` (100), `DEFAULT_CURRENCY` (`BRL`) |
| `cache_constants.py` | `CACHE_KEY_PREFIX`, `DEFAULT_CACHE_TTL_SECONDS` (300), `SHORT_CACHE_TTL_SECONDS` (60), `LONG_CACHE_TTL_SECONDS` (3600) — usadas a partir da Fase 9 (Redis) |
| `message_constants.py` | Mensagens PT-BR: `RESOURCE_NOT_FOUND`, `VALIDATION_ERROR`, `BUSINESS_RULE_VIOLATION`, `INTERNAL_SERVER_ERROR`, `UNAUTHORIZED`, `FORBIDDEN` |

### 6.3 `shared/enums/`

Pacote reservado para **enumerações transversais** (compartilhadas por 2+ módulos). Na Fase 2
contém apenas `__init__.py` — será preenchido conforme os enums de domínio surgirem.

---

## ⚙️ 7. `config/` como pacote + `dependencies/`

`config` é um **pacote** (não um módulo único), o que permite crescer sem quebrar o import
público `from energyhub.config import settings`.

- **`config/settings.py`** — define `Settings(BaseSettings)` (pydantic-settings), carregado de
  variáveis de ambiente e de `.env`:

  | Campo | Tipo | Default |
  | :---- | :--- | :------ |
  | `app_name` | `str` | `"EnergyHub"` |
  | `debug` | `bool` | `False` |
  | `database_url` | `str` | `postgresql+asyncpg://energyhub:energyhub123@localhost:5432/energyhub` |
  | `secret_key` | `str` | `"change-me-in-production"` |
  | `algorithm` | `str` | `"HS256"` |
  | `access_token_expire_minutes` | `int` | `30` |

  Fornece `get_settings()` (memoizado com `@lru_cache`) e uma instância de módulo `settings`.
  `model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")`.

- **`config/__init__.py`** — reexporta a API estável:
  `from energyhub.config.settings import Settings, get_settings, settings`
  (mantém `from energyhub.config import settings` funcionando).

- **`config/dependencies/`** — pacote de **injeção de dependência** (FastAPI `Depends`). Na Fase 2
  contém apenas `__init__.py` (vazio, documentado). Será preenchido nas fases seguintes com
  provedores de `AsyncSession`, repositórios, serviços e usuário autenticado.

---

## 💎 8. Modelo de Domínio (Fase 3)

A **Fase 3** (versão `0.3.0`) preencheu a camada `domain` dos 8 módulos de negócio com **domínio
puro**: **13 entidades**, **8 enums**, **6 _value objects_**, **5 agregados** e **3 exceções de
domínio** — nada disso importa framework (só biblioteca-padrão). O mapeamento ORM (modelos
SQLAlchemy + `relationship()`) fica para a **Fase 5**; até lá, os relacionamentos entre entidades
são **referências Python** em memória.

### 8.1 🧩 Entidades e enums por módulo

Cada entidade estende `BaseEntity` como `@dataclass(kw_only=True)`; os enums são `(str, Enum)`.
Ambos vivem em `<módulo>/domain/entity/`.

| Módulo | Entidades | Enums |
| :----- | :-------- | :---- |
| `auth` | `User`, `Role`, `Permission` | — |
| `clients` | `Client`, `Contact` | `ContactType` |
| `contracts` | `Contract` | `ContractStatus`, `ContractType` |
| `negotiations` | `Negotiation`, `EnergyTransaction` | `NegotiationStatus`, `TransactionType` |
| `financial` | `Invoice`, `Payment` | `InvoiceStatus` |
| `audit` | `AuditLog` | `AuditAction` |
| `notifications` | `Notification` | `NotificationStatus` |
| `reports` | `Report` | — |
| **Total** | **13 entidades** | **8 enums** |

### 8.2 💠 Value Objects (`shared/domain/valueobject/`)

Os 6 _value objects_ são **frozen dataclasses** (imutáveis). Os que exigem validação a fazem no
`__post_init__`, levantando **`ValueError`** quando o dado é inválido (VOs **não** dependem de
`ValidationException` nem de Pydantic):

| VO | Campos | Validação / normalização |
| :- | :----- | :------------------------ |
| `CNPJ` | `value: str` | dígitos verificadores (algoritmo da Receita); guarda só os 14 dígitos; `formatted()` → `XX.XXX.XXX/XXXX-XX` |
| `Email` | `value: str` | exige `@` e normaliza para minúsculas |
| `PhoneNumber` | `value: str` | mantém só os dígitos; exige de 10 a 13 |
| `Percentage` | `value: Decimal` | intervalo `0 ≤ value ≤ 100` |
| `Money` | `amount: Decimal`, `currency: str = "BRL"` | valor monetário com moeda (Decimal para precisão) — estrutura imutável, sem validação |
| `Address` | `street`, `city`, `state`, `zip_code`, `country="Brasil"` | endereço postal estruturado — estrutura imutável, sem validação |

### 8.3 🧱 Agregados e exceções de domínio

Os **5 agregados** vivem em `<módulo>/domain/<x>_aggregate.py` — classes simples que encapsulam uma
**raiz** e delegam as regras de negócio a ela (fronteira de consistência):

| Agregado | Raiz | Fronteira de consistência |
| :------- | :--- | :------------------------ |
| `AuthAggregate` | `User` | `Role` (via `add_role`/`remove_role`) |
| `ClientAggregate` | `Client` | `Contact` (via `add_contact`/`remove_contact`) |
| `ContractAggregate` | `Contract` | transições de estado (`approve`/`activate`) |
| `NegotiationAggregate` | `Negotiation` | `EnergyTransaction` |
| `FinancialAggregate` | `Invoice` | `Payment` |

As **3 exceções de domínio** estendem `DomainException` diretamente, em `<módulo>/domain/exception/`:
`InvalidContractStatusException` (contracts), `InvalidClientStateException` (clients) e
`InvalidNegotiationException` (negotiations).

### 8.4 🧬 Padrões do domínio puro

- **Entidades** — `@dataclass(kw_only=True)` estendendo `BaseEntity`. A validação roda no
  `__post_init__` (que chama `super().__post_init__()` primeiro) e levanta **`ValidationException`**
  em vez de usar validadores Pydantic. Ex.: `Contract.__post_init__` recusa `end_date < start_date`
  e valores negativos.
- **Relacionamentos** — são **referências Python**: listas via
  `field(default_factory=list, compare=False, repr=False)` (ex.: `User.roles`, `Client.contacts`) e
  refs opcionais via `field(default=None, compare=False, repr=False)` (ex.: `Contract.client`). O
  `compare=False, repr=False` evita **recursão** em `__eq__`/`__repr__` entre entidades ligadas nos
  dois sentidos, e os imports das entidades relacionadas ficam sob `if TYPE_CHECKING:` para não criar
  ciclos de importação.
- **Métodos de negócio na raiz** — `Contract.approve()` exige status `PENDING_APPROVAL` → `APPROVED`;
  `Contract.activate()` exige `APPROVED` + `start_date` não futura → `ACTIVE` (ambos levantam
  `InvalidContractStatusException`). `User.add_role`/`remove_role` mantêm a relação `User`↔`Role`
  bidirecional; `Role.add_permission`/`remove_permission` gerenciam as permissões.
- **Value Objects** — frozen dataclasses que levantam `ValueError` (ver 8.2).
- **ORM adiado** — nenhum modelo SQLAlchemy ou `relationship()` no domínio; o mapeamento ORM e a
  persistência dos relacionamentos entram na **Fase 5**.

---

## 🗄️ 9. Schema do Banco e Migrações (Fase 4)

A **Fase 4** (versão `0.4.0`) materializou o **schema PostgreSQL** que dará lastro ao modelo de
domínio, de forma **versionada e reversível** via **Alembic**. Ainda **não há modelos ORM** (isso é a
Fase 5): as migrações são **escritas à mão** (`op.create_table`, `op.create_index`, `op.execute`),
não geradas por _autogenerate_ (não haveria metadata para comparar sem os modelos).

### 9.1 ⚙️ Configuração do Alembic

- **`alembic.ini`** (na raiz do projeto Poetry) — `script_location = alembic`,
  `prepend_sys_path = src`, `file_template` com timestamp UTC e `timezone = UTC`. A `sqlalchemy.url`
  é apenas um _placeholder_, sobrescrito em tempo de execução.
- **`alembic/env.py`** — **fonte única** de configuração: importa `settings.database_url` e
  `Base.metadata`. Suporta migração **online** (engine assíncrono `asyncpg` com `NullPool`, via
  `connection.run_sync`) e **offline** (`literal_binds`, gera SQL sem conectar ao banco).
- **`Base`** (`shared/infrastructure/persistence/database.py`) — `DeclarativeBase` compartilhada; sua
  `metadata` é o `target_metadata` do Alembic. Permanece vazia até os modelos ORM serem mapeados na
  Fase 5.

### 9.2 🧱 Migrações e tabelas

**9 migrações encadeadas** (`0001`→`0009`), cada uma com `downgrade` simétrico:

| Revisão | Conteúdo |
| :-----: | :------- |
| `0001` | `pgcrypto` + auth (`users`, `roles`, `permissions`, `user_roles`, `role_permissions`), `clients`, `contacts`, `contracts` + índices _inline_ |
| `0002` | `negotiations`, `energy_transactions` |
| `0003` | `invoices`, `payments` |
| `0004` | `audit_logs` |
| `0005` | `notifications`, `reports` |
| `0006` | índices compostos e temporais |
| `0007` | CHECK constraints + função/triggers `updated_at` |
| `0008` | _seed_ (papéis, 4 permissões `USER_*`, grants, usuário admin) |
| `0009` | _seed_ do **catálogo completo** de permissões (34 novas → 38 no total) + concede **todas** ao `ADMIN` (Fase 7) |

**15 tabelas** de domínio no total. Convenções: **PK UUID** com `server_default gen_random_uuid()`;
`created_at`/`updated_at` `TIMESTAMP WITH TIME ZONE` default `CURRENT_TIMESTAMP`; valores monetários e
quantidades em `Numeric` (nunca ponto flutuante); `JSONB` para `details`/`parameters`.

### 9.3 🔗 Chaves estrangeiras, índices e constraints

- **FKs — `ON DELETE`:** **CASCADE** para filhos _owned_ (`contacts`→`clients`,
  `energy_transactions`→`negotiations`, `payments`→`invoices`, `notifications`→`users`, e os _joins_
  `user_roles`/`role_permissions`); **RESTRICT** para referências protegidas (`contracts`→`clients`,
  `invoices`→`clients`, `negotiations`→`contracts`, `audit_logs`→`users`, `reports`→`users`) — para
  nunca perder silenciosamente registros contratuais, financeiros ou de auditoria.
- **42 índices:** únicos nos identificadores de negócio (`username`, `email`, `cnpj`,
  `contract_number`, ...); simples em colunas de _lookup_/FK; compostos em
  `contracts(client_id, status)` e `contracts(start_date, end_date)`; temporais em
  `audit_logs.created_at` e `notifications.created_at`.
- **4 CHECK constraints:** formato de e-mail e de CNPJ (formatado ou 14 dígitos),
  `end_date > start_date` e valores de contrato estritamente positivos — **alinhados com a validação
  do domínio** (o `Contract` foi endurecido na Fase 4 para a mesma regra, ver Seção 8.4).
- **`updated_at` automático:** função `update_updated_at_column()` + **13 triggers** `BEFORE UPDATE`
  (um por tabela com `updated_at`), garantindo o carimbo independentemente do caminho de escrita.

### 9.4 🌱 Seed e verificação

O _seed_ (revisão `0008`, idempotente com `ON CONFLICT DO NOTHING`) insere 3 papéis
(`ADMIN`/`OPERATOR`/`CLIENT`), 4 permissões `USER_*`, os grants do ADMIN e o usuário **`admin`** (hash
**bcrypt**, UUIDs fixos). A revisão **`0009`** (Fase 7) completa o catálogo para **38 permissões** e
concede **todas** ao `ADMIN` via `INSERT…SELECT` idempotente. ⚠️ Credencial de _bootstrap_ —
**rotacionar antes de produção** (junto com o `SECRET_KEY`).

Validado contra o **PostgreSQL do Docker**: `upgrade head` cria **16 tabelas** (15 + `alembic_version`,
agora em `0009`); os cenários de CHECK/unicidade/FK (CASCADE e RESTRICT) e o trigger de `updated_at` se
comportam como esperado; e o _round-trip_ `downgrade base` → `upgrade head` volta ao schema completo
sem erros de FK. Gates limpos: `ruff` / `black` / `mypy` (em `src` e `alembic`).

> 🪟 **Nota Windows/Docker Desktop:** conexões do _host_ ao Postgres do container costumam falhar no
> _port-proxy_. Nesses casos, aplique as migrações gerando o SQL **offline** e passando-o ao `psql`
> dentro do container:
> `poetry run alembic upgrade head --sql | docker compose exec -T postgres psql -U energyhub -d energyhub`.

---

## 🗃️ 10. Persistência (Fase 5)

A **Fase 5** (versão `0.5.0`) adicionou a camada de acesso a dados **async** sobre o schema da Fase 4,
**sem** acoplar o domínio ao SQLAlchemy.

### 10.1 🔌 Configuração (`shared/infrastructure/persistence/database.py`)

- **`Base`** — `DeclarativeBase` cuja `metadata`/`registry` ancora o mapeamento.
- **`engine`** — `create_async_engine(settings.database_url, echo=settings.debug)` (driver `asyncpg`).
- **`async_session_maker`** — `async_sessionmaker(..., expire_on_commit=False)` (atributos seguem
  acessíveis após o commit).
- **`get_session()`** — dependência que cede uma `AsyncSession` e a fecha ao final.

### 10.2 🧩 Mapeamento imperativo (domínio puro)

As entidades da Fase 3 continuam _dataclasses_ **puras**. Em vez de torná-las modelos declarativos
(o que traria SQLAlchemy para o domínio), o mapeamento é **imperativo** em
`shared/infrastructure/persistence/mapping.py`:

```python
users_table = Table("users", metadata, Column("id", UUID, primary_key=True), ...)
registry.map_imperatively(User, users_table, properties={
    "roles": relationship(Role, secondary=user_roles_table, back_populates="users"),
})
```

`configure_mappings()` registra os 13 mappers + associações e chama `configure_mappers()` no
**startup** (em `main.py`) e nos testes. Depois disso, os repositórios consultam as entidades direto
(`select(User).where(User.username == ...)`), pois o mapper as instrumenta.

- **Igualdade por identidade:** para o ORM, `BaseEntity` usa `eq=False` + `__eq__`/`__hash__` por
  `id` (semântica de _entidade_ em DDD; instâncias hasheáveis).
- **Custo do mapeamento imperativo:** o mypy não enxerga a instrumentação nas _dataclasses_, então as
  queries geram falsos positivos; suprimidos por um _override_ de mypy escopado a
  `*.infrastructure.persistence.*` — o restante do código segue sob mypy estrito.
- **Alinhamento com a Fase 4:** as `Table`s espelham as migrações (fonte de verdade); sem
  `--autogenerate`.

### 10.3 📚 Repositórios, filtros e paginação

- **`SQLAlchemyRepository[T, ID]`** — CRUD genérico: `save` (add + **flush**, sem commit — a transação
  pertence ao _use case_), `find_by_id`, `find_all`, `delete_by_id`, `exists_by_id`, além de
  `find_by(*conditions)` e `find_page(offset, limit, *conditions) -> (conteúdo, total)`.
- **13 repositórios concretos** (`<módulo>/infrastructure/persistence/`) — um por entidade, com
  _finders_ específicos (ex.: `UserRepository.find_by_username`, `ClientRepository.find_by_cnpj`,
  `ContractRepository.find_by_status`).
- **Filtros componíveis** — `ClientFilter`/`ContractFilter` retornam condições SQLAlchemy;
  `*.search(dto)` traduz um **DTO de filtro Pydantic** (`ClientFilterDTO`/`ContractFilterDTO`,
  em `<módulo>/application/dto/`) em predicados combinados por `and_`.
- **Paginação** (`shared/application/dto/`) — `PageRequest` (zero-based, `size` limitado a
  `MAX_PAGE_SIZE`, `get_offset()`/`get_limit()`) e `PageResponse[T].create(...)` (calcula
  `total_pages`/`first`/`last`). O repositório devolve `(conteúdo, total)` e a montagem do
  `PageResponse` fica na aplicação — a infraestrutura não depende da aplicação.

> 🧪 **Testes:** a suíte de integração roda contra o Postgres do Docker com isolamento por _rollback_
> (o `save` faz _flush_, não _commit_). No Windows, conexões do host ao container falham; rode os
> testes **dentro da rede do compose** (mesma abordagem da Fase 4).

---

## 🌐 11. Aplicação & Apresentação — API REST (Fase 6)

A **Fase 6** (versão `0.6.0`) preencheu as camadas `application` e `presentation` de cada módulo,
expondo as entidades persistidas como uma **API REST** documentada. O fluxo por módulo é uma cadeia
de responsabilidades:

```
Router (HTTP) → UseCase (orquestração) / Service (regras) → Mapper (entidade↔DTO) → Repository (Fase 5)
```

### 11.1 🧱 As cinco peças

| Peça | Local | Papel |
| :--- | :---- | :---- |
| **Request/Response DTO** | `<módulo>/application/dto/` | Pydantic. _Request_ estende `BaseModel`; _response_ estende `BaseDTO` (auditoria + `from_attributes`). Relações são **DTOs aninhados** (ex.: `UserResponseDTO.roles`). |
| **Validators** | `shared/application/validation/validators.py` | `validate_cnpj`/`validate_email`/`validate_non_empty`, aplicados nos DTOs via `@field_validator`. |
| **Mapper** | `<módulo>/application/mapper/` | `to_entity(dto)` e `to_response_dto(entity)` (= `ResponseDTO.model_validate(entity)`). Ponto único de tradução. |
| **Service** | `<módulo>/application/service/` | Regras de negócio: unicidade, hashing de senha, resolução de ids, CRUD paginado. Faz `flush` via repositório; nunca `commit`. |
| **Use Case** | `<módulo>/application/usecase/` | `UseCase[Input, Output]` fino, delega ao service (ex.: `CreateUserUseCase`). |
| **Router** | `<módulo>/presentation/router/` | `BaseRouter` sob `/api/v1/<recurso>`; endpoints com _providers_ `Depends(get_session)` → repositório → service. |

`BaseDTO` e `PageResponse` foram migrados de _dataclass_ para **Pydantic** nesta fase (herança de
auditoria e uso como `response_model` nas listagens).

### 11.2 🔀 Exceções → HTTP e a unidade de trabalho

- **Exceções de domínio** por módulo (`<módulo>/domain/exception/`) estendem as bases compartilhadas:
  _not-found_ → `ResourceNotFoundException`, _already-exists_ → `BusinessRuleException`,
  _invalid_ → `ValidationException`. Um **handler central**
  (`shared/presentation/exception/domain_exception_handler.py`), registrado para `DomainException`,
  traduz por tipo em **404 / 409 / 422** (com `ErrorResponse` padronizado).
- **Transação na borda:** `get_session()` (Fase 5) agora faz `commit` ao final da requisição e
  `rollback` em erro. Como os serviços só dão `flush`, várias operações de um request compõem **uma
  transação** (a fronteira da unidade de trabalho fica no `get_session`).

### 11.3 ⚠️ Padrões impostos pelo ORM async

Como as entidades são _dataclasses_ puras mapeadas imperativamente (Fase 5), a Fase 6 fixou alguns
padrões para evitar armadilhas do async + relações:

- **Respostas usam FK ids, não objetos-pai aninhados** (ex.: `ContractResponseDTO.client_id`, sem
  `client`). Coleções **filhas** aparecem aninhadas (contatos, papéis) e são carregadas por
  `lazy="selectin"`.
- **Relações de navegação são `viewonly=True`** no mapeamento; escritas de FK ocorrem só pela coluna
  (ex.: `Contact(client_id=...)`). Sem isso o _flush_ zerava a FK (`UPDATE→NULL`). Escritas **M2M**
  (papéis/permissões) usam a relação real.
- **Sub-recursos** (`/clients/{id}/contacts`, `/invoices/{id}/payments`,
  `/negotiations/{id}/transactions`) recebem a FK do **path**: `service.create(parent_id, dto)`.
- **Segurança:** a senha do usuário é hasheada no service (`shared/infrastructure/security/`,
  `bcrypt`) e **nunca** exposta em DTO de resposta.

### 11.4 🗺️ Superfície da API (10 routers · 25 endpoints)

`/api/v1/` → `users` · `roles` · `permissions` (auth) · `clients` (+ `/{id}/contacts`) · `contracts` ·
`negotiations` (+ `/{id}/transactions`) · `invoices` (+ `/{id}/payments`) · `audit-logs`
(append-only) · `notifications` · `reports`. Documentação interativa em **`/docs`** e **`/redoc`**.

---

## 🔒 12. Segurança — Autenticação & Autorização (Fase 7)

A **Fase 7** (versão `0.7.0`) adicionou a camada de segurança **sobre** a API da Fase 6: identidade
verificada por **JWT** e acesso controlado por **papéis/permissões (RBAC)**, tudo expresso como
**dependências do FastAPI** anexadas às rotas (não um _middleware_ global). O corte por camada segue a
regra de dependência: hashing e _guards_ são transversais e vivem em `shared`; JWT e carregamento do
usuário são específicos de auth e vivem em `auth`.

### 12.1 🧱 As peças

| Peça | Local | Papel / assinatura-chave |
| :--- | :---- | :----------------------- |
| `get_password_hash` / `verify_password` | `shared/infrastructure/security/password_hasher.py` | Hash BCrypt (custo 12; trunca a 72 bytes). `hash_password` é _alias_ retrocompat. |
| `JwtService` | `auth/infrastructure/security/jwt_service.py` | HS256 a partir das _settings_: `create_token(subject, claims)`, `decode_token`, `extract_username`, `is_token_valid`. |
| `LoginRequestDTO` / `LoginResponseDTO` | `auth/application/dto/` | Credenciais e retorno (`access_token`, `token_type="bearer"`, `user`). |
| `AuthenticationService` | `auth/application/service/authentication_service.py` | `login(dto)`: valida credenciais e emite o token; rejeita inexistente/senha errada/inativo com o **mesmo** erro. |
| `AuthRouter` | `auth/presentation/router/auth_router.py` | Rota **pública** `POST /api/v1/auth/login`. |
| `UserDetails` | `auth/infrastructure/security/user_details.py` | Wrapper do `User`: `username`, `active`, `roles` (nomes), `permissions` (achatadas). |
| `get_current_user` | `auth/infrastructure/security/current_user.py` | Dependência: `HTTPBearer(auto_error=False)` → `extract_username` → recarrega o usuário → `UserDetails`. |
| `require_permission` / `require_role` | `shared/infrastructure/security/authorization.py` | _Factories_ de dependência (encadeiam `get_current_user`) → **403** se faltar o grant. |
| Catálogo de permissões | `shared/constant/permissions.py` | 38 nomes canônicos `<RECURSO>_<AÇÃO>` + `PERMISSION_CATALOG`. |

### 12.2 🔑 Fluxo de autenticação

1. `POST /api/v1/auth/login` (público) → `AuthenticationService.login` acha o usuário por `username`,
   confere a senha com `verify_password` e a conta ativa; em falha, `InvalidCredentialsException`.
2. Um **handler dedicado** traduz `InvalidCredentialsException` em **401** com `WWW-Authenticate: Bearer`
   (mais específico, na MRO, que o handler de domínio que a mapearia para 422).
3. Em sucesso, `JwtService.create_token(username)` emite o JWT (claim `sub`=username, `exp`); a resposta
   traz o token + o perfil (`UserResponseDTO`, **sem** senha).
4. Nas rotas protegidas, `get_current_user` lê o `Bearer`, extrai o `sub` e **recarrega** o usuário
   (papéis/permissões vêm _eager_ via `lazy="selectin"`) — token ausente/inválido ou _subject_ sem
   usuário → **401**. Recarregar a cada request mantém a autorização fresca quando os grants mudam.

### 12.3 🛡️ Autorização (RBAC) e proteção dos endpoints

- **Guards:** `require_permission("CLIENT_CREATE")` / `require_role("ADMIN")` dependem de
  `get_current_user`, então **401 (não autenticado)** é sempre resolvido **antes** de **403 (sem
  permissão)**. `UserDetails.permissions` achata os nomes de permissão por todos os papéis do usuário.
- **Proteção em dois níveis:** cada router de recurso passa `dependencies=[Depends(get_current_user)]`
  no `super().__init__(...)` (proteção de **grupo**) **e** anexa `dependencies=[Depends(require_permission(<PERM>))]`
  por endpoint (mapeando CRUD → permissão). Sub-recursos reutilizam a permissão do pai; `audit-logs` é
  append-only (`AUDIT_LOG_CREATE`/`_READ`).
- **Superfície:** **54 operações** exigem JWT + permissão; apenas `POST /api/v1/auth/login`, `/` e
  `/health` são públicos. O esquema de segurança do OpenAPI é `bearerAuth` (botão **Authorize** no
  `/docs`; nomeado assim na Fase 8, ver Seção 13).
- **Dados de grant:** a migração `0009` semeia as **38 permissões** e concede **todas** ao `ADMIN`
  (`INSERT…SELECT`, à prova de futuro). `OPERATOR`/`CLIENT` ficam sem grants até uma fase futura.

### 12.4 ⚠️ Decisões e desvios

- **BCrypt direto (não `passlib`):** o plano previa um `passlib` `CryptContext`, mas o `passlib` 1.7.4
  é incompatível com o `bcrypt 5.x` instalado (estoura ao ler `bcrypt.__about__`). Preservou-se a
  _intenção_ da spec com a lib `bcrypt` diretamente — documentado no módulo.
- **`python-jose` sem stubs:** _override_ de mypy `module=["jose.*"] ignore_missing_imports=true`; os
  tipos de retorno são fixados no `JwtService`.
- **Seed do catálogo (0009):** desvio consciente do _non-goal_ "sem mudanças no seed" da Fase 7 — sem
  as permissões semeadas os _guards_ não teriam grants para verificar e a API ficaria inutilizável.
- **JWT _stateless_ (HS256):** sem sessão/servidor de estado; token só de acesso (sem _refresh_/revogação
  nesta fase) — manter `access_token_expire_minutes` modesto.

### 12.5 🧪 Como proteger um novo endpoint

```python
from fastapi import Depends
from energyhub.auth.infrastructure.security.current_user import get_current_user
from energyhub.shared.constant.permissions import CLIENT_CREATE
from energyhub.shared.infrastructure.security.authorization import require_permission

class ClientRouter(BaseRouter):
    def __init__(self) -> None:
        # proteção de grupo: todo endpoint deste router exige um JWT válido
        super().__init__(prefix=f"{API_V1_PREFIX}/clients", tags=["clients"],
                         dependencies=[Depends(get_current_user)])
        ...

    @router.post("", dependencies=[Depends(require_permission(CLIENT_CREATE))])
    async def create(...): ...
```

Para uma permissão nova, adicione a constante em `shared/constant/permissions.py`, semeie-a numa nova
migração e conceda-a ao(s) papel(is) — os _guards_ passam a reconhecê-la automaticamente.

---

## 📘 13. Documentação & Erros da API (Fase 8)

A **Fase 8** (versão `0.8.0`) tornou a API **auto-descritiva**: metadados OpenAPI curados, endpoints
e DTOs documentados, e corpos de erro **padronizados** — sem alterar o comportamento das rotas de
sucesso (apenas a forma dos erros passou a ser garantida).

### 13.1 🧾 OpenAPI customizado (`main.py`)

`app.openapi` é substituído por um `custom_openapi()` que constrói o schema **uma vez** (cacheado em
`app.openapi_schema`) e injeta:

- **Metadados** — `contact` e `license` em `info`, além de `title`/`description`/`version` (`0.8.0`).
- **Segurança** — o esquema `bearerAuth` (`type: http`, `scheme: bearer`, `bearerFormat: JWT`) em
  `components.securitySchemes` + um requisito de segurança **global** (`security: [{bearerAuth: []}]`).
  As rotas **públicas** (`/api/v1/auth/login`, `/`, `/health`) têm `security: []` (neutralizado). O
  `HTTPBearer` da Fase 7 foi nomeado `bearerAuth` (via `scheme_name`) para unificar com este esquema.
- **Tags** — `openapi_tags` com **12 grupos** descritos (`Authentication`, `Users`, `Clients`, …);
  cada router declara sua tag, agrupando as operações no Swagger UI (`/docs`) e ReDoc (`/redoc`).

### 13.2 🏷️ Documentação de endpoints e DTOs

- **Rotas** — cada operação declara `summary`, `description` e `responses` por status. Os blocos de
  erro reutilizáveis vivem em `shared/presentation/response/openapi_responses.py` (`BAD_REQUEST`,
  `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `AUTH_ERRORS`) e são compostos por rota (ex.:
  um `POST` de criação com unicidade usa `{**BAD_REQUEST, **CONFLICT, **AUTH_ERRORS}`). Assim o que é
  **documentado** aponta para os mesmos modelos que os handlers **emitem**.
- **DTOs** — cada campo usa `Field(description=..., examples=[...])` e _constraints_ leves
  (`min_length`/`max_length`/`gt`) que espelham a validação de domínio. E-mails permanecem `str` +
  `@field_validator` (o pacote `email-validator` do `EmailStr` **não** está instalado).

### 13.3 🚦 Corpos de erro padronizados

Dois modelos Pydantic em `shared/presentation/response/`, documentados no OpenAPI:

| Modelo | Quando | Campos |
| :----- | :----- | :----- |
| `ErrorResponse` | `4xx`/`5xx` gerais | `timestamp`, `status`, `error`, `message`, `path`, `error_code?` |
| `ValidationErrorResponse` | validação de _schema_ (400) | `status`, `message`, `errors: [FieldError{field, message}]` |

Handlers (registrados em `main.py`) alinhados aos modelos:

| Origem | Status | Corpo |
| :----- | :----: | :---- |
| `RequestValidationError` (Pydantic) | **400** | `ValidationErrorResponse` (um `FieldError` por campo) |
| `ResourceNotFoundException` | 404 | `ErrorResponse` |
| `BusinessRuleException` (ex.: já-existe) | 409 | `ErrorResponse` |
| `ValidationException` de domínio | 422 | `ErrorResponse` |
| `InvalidCredentialsException` | 401 | `ErrorResponse` + `WWW-Authenticate: Bearer` |
| Exceção não tratada | **500** | `ErrorResponse` (mensagem genérica) |

> ⚠️ **400 × 422:** validações feitas por `@field_validator` do DTO (CNPJ, e-mail, não-vazio) falham
> na camada de _schema_ → **400**; violações levantadas no domínio/serviço → **422**.

### 13.4 🔑 `error_code` e catálogo

`DomainException` expõe `error_code: ClassVar[str]` (default `DOMAIN_ERROR`); cada subclasse
sobrescreve com um código estável (`CLIENT_NOT_FOUND`, `INVALID_CNPJ`, …). Os handlers ecoam o
`error_code` no corpo, e o catálogo completo (status + código por módulo) vive em
[`docs/API_ERRORS.md`](./API_ERRORS.md). Exemplos `curl` ponta-a-ponta em
[`docs/API_EXAMPLES.md`](./API_EXAMPLES.md).

---

## ⚡ 14. Cache de Leitura (Redis · Fase 9)

A **Fase 9** (versão `0.9.0`) adicionou um **read-cache** Redis via `fastapi-cache2`, servindo leituras
repetidas da memória e invalidando entradas em cada escrita. O cache é um **acelerador**: os serviços
permanecem corretos sem ele.

### 14.1 🧱 As peças

| Peça | Local | Papel |
| :--- | :---- | :---- |
| Serviço Redis | `docker-compose.yml` | `redis:7-alpine` (append-only, volume `redis_data`, healthcheck `redis-cli ping`). |
| Settings | `config/settings.py` | `redis_host`/`redis_port`/`redis_db`/`redis_password` + `redis_url` (propriedade derivada). |
| `CacheConfig` | `shared/infrastructure/cache/cache_config.py` | `init_cache()` (RedisBackend + prefixo `energyhub` + **PickleCoder**) chamado no **lifespan**; `get_cache_key()` + key builders (`id_key_builder`, `page_key_builder`). |
| `CacheConstants` | `shared/constant/cache_constants.py` | Namespaces por domínio + TTLs `SHORT`/`DEFAULT`/`LONG`. |
| Invalidação | `shared/infrastructure/cache/cache_helper.py` | `invalidate_cache(namespace, key?)` e `invalidate_all_cache()`. |
| `CacheRouter` | `shared/presentation/router/cache_router.py` | `/api/v1/cache` (`GET /stats`, `POST /clear`) sob `CACHE_MANAGE`. |

### 14.2 🔑 Padrão de cache nos serviços

Os métodos de **leitura** dos serviços (Role, Permission, Client, Contract, User) são decorados:

```python
@cache(namespace=CacheConstants.ROLES, expire=CacheConstants.LONG_TTL, key_builder=id_key_builder)
async def find_by_id(self, role_id: UUID) -> RoleResponseDTO: ...
```

- **`PickleCoder`** (default do `init_cache`) faz o *round-trip* fiel dos **DTOs Pydantic** (a leitura
  cacheada devolve o mesmo tipo, não um `dict`).
- Os **key builders ignoram o `self`** do serviço (`args[1:]`), produzindo chaves estáveis como
  `energyhub:roles:{id}` e `energyhub:roles:all:{page}:{size}:{sort}:{direction}`.
- **TTL por volatilidade:** dados de referência (papéis/permissões) usam `LONG_TTL`; clientes, `SHORT_TTL`.

### 14.3 ♻️ Invalidação na escrita

Todo `create`/`update`/`delete` chama `await invalidate_cache(CacheConstants.<NS>)` após o `save`/`delete`
do repositório, evictando o namespace do domínio — a próxima leitura repopula com dado fresco. O
`invalidate_all_cache()` (usado no `POST /clear`) remove todas as chaves `energyhub:*`.

### 14.4 ⚠️ Notas e limitações

- **Best-effort, mas requerido:** nesta fase os erros de cache **propagam** (sem *fail-open*); o Redis do
  compose é dependência de runtime dos caminhos cacheados. *Fail-open* fica como evolução.
- **Tipos:** o `@cache` tipa o retorno como `T | Response` (uso em endpoints); nos routers finos isso é
  silenciado por um _override_ de mypy `[return-value]` (o `response_model` valida a saída real).
- **Deps:** `fastapi-cache2` fixa `redis<5` (usamos `redis ^4.6`) e importa `starlette.templating`
  (exige `jinja2`). No Windows, o Redis **conecta do host** (ao contrário do Postgres).

---

## 📨 15. Mensageria Assíncrona (RabbitMQ & Kafka · Fase 10)

A **Fase 10** (versão `0.10.0`) introduziu uma **camada de mensageria** para comunicação orientada a
eventos **fora do caminho da requisição**: dois brokers por forma de tráfego — **RabbitMQ** para
_workflows_ por entidade (roteamento a um consumidor + at-least-once) e **Kafka** para _streams_ de
alto volume (partições + consumer groups). A publicação é um **efeito colateral pós-commit**: os
serviços permanecem corretos sem os brokers.

### 15.1 🧱 As peças

Tudo em `shared/infrastructure/messaging/` (base) + `<módulo>/infrastructure/messaging/` (por domínio):

| Arquivo | Papel |
| :------ | :---- |
| `rabbitmq_config.py` | `RabbitMQConfig` (constantes de **11 filas** + `get_url()`) e `setup_queues()` — declara todas duráveis, idempotente |
| `event_producer.py` | `EventProducer` base — conexão robusta preguiçosa, `publish(queue, message)` **persistente** (`DeliveryMode.PERSISTENT`) no _default exchange_ |
| `auth/.../user_event_producer.py`, `clients/.../client_event_producer.py` | Produtores por módulo (subclasses tipadas) + instância _singleton_ compartilhada |
| `notifications/.../notification_consumer.py`, `audit/.../audit_consumer.py` | Consumidores (`prefetch_count=1`, ack pós-processo); `AuditConsumer` persiste um `AuditLog` |
| `audit_event.py` | `AuditEvent` — contrato Pydantic tipado da mensagem de auditoria |
| `kafka_config.py` | `KafkaConfig` (**4 tópicos** com partições/replicação) + `create_topics()` idempotente |
| `kafka_event_producer.py` / `kafka_event_consumer.py` | `KafkaEventProducer` (keyed `send_and_wait`) / `KafkaEventConsumer` (por tópico, `stop` no `finally`) + _singleton_ |
| `publish_helper.py` | `publish_safely` — loga e engole `MessagePublishingException` sem desfazer a escrita |
| `shared/domain/exception/message_publishing_exception.py` | `MessagePublishingException` (`error_code="MESSAGE_PUBLISHING_ERROR"`) |

A **topologia** (filas + tópicos) é preparada no **`lifespan`** da app (idempotente, _best-effort_: um
broker indisponível apenas gera aviso e não derruba o startup); os produtores _singleton_ são
encerrados no shutdown. Config única via `settings` (`rabbitmq_url`, `kafka_bootstrap_servers`,
`kafka_group_id`).

### 15.2 📤 Padrão de produção nos serviços (pós-commit)

Os produtores são injetados (opcionais) nos serviços e chamados **após** a escrita persistida:

```python
saved = await self._repository.save(entity)
await invalidate_cache(CacheConstants.CLIENTS)
response = self._mapper.to_response_dto(saved)
if self._producer is not None:                        # RabbitMQ (User/Client)
    await publish_safely(
        self._producer.publish_client_created(response), event="client.created"
    )
return response
```

`ContractService`/`InvoiceService` publicam no **Kafka** (`contract-events`/`financial-events`) sob a
**chave = id** (mesma chave → mesma partição → ordem preservada). `publish_safely` garante que uma
falha de broker vire log, não `rollback` — a mensageria é _downstream_ da fonte de verdade.

### 15.3 📥 Consumidores e garantias de entrega

- **`NotificationConsumer`** assina `user.created`/`client.created`/`contract.approved`/`invoice.issued`;
  **`AuditConsumer`** consome `audit` e persiste um `AuditLog` (sessão própria + `commit`, pois roda
  off-request). Ambos: `prefetch_count=1` e ack **dentro** de `message.process()` — ack só no sucesso.
- **At-least-once:** um handler que falha/é interrompido causa **redelivery** (`requeue=True`).
- **Durabilidade:** filas `durable=True` + mensagens persistentes **sobrevivem ao restart** do broker.
- **Isolamento da transação:** um broker fora do ar durante a publicação surge como
  `MessagePublishingException` (logada) **sem** desfazer o estado commitado.

### 15.4 ⚠️ Notas e limitações

- **Consumidores não-supervisionados nesta fase:** o comportamento está especificado e validado, mas
  a execução dos processos consumidores (entrypoint/worker) é tarefa de _ops_ (fase posterior).
- **Dual-write aceito:** sem _outbox_ transacional — um evento pode se perder se o broker cair após o
  commit; consumidores devem tolerar duplicatas. _Outbox_ fica como evolução.
- **Deps/tipos:** `aio-pika ^9.4` (tipado; o canal é `AbstractChannel`) e `aiokafka ^0.11` (sem stubs
  → _override_ de mypy `aiokafka.*`). Kafka no compose usa dois _listeners_ (`localhost:9092` host /
  `kafka:29092` rede) e `auto-create` desligado. No Windows, **RabbitMQ e Kafka conectam do host**.

---

## 🔎 16. Busca Full-Text (Elasticsearch · Fase 11)

A **Fase 11** (versão `0.11.0`) adicionou um **subsistema de busca** sobre Elasticsearch: busca
_full-text_ com relevância, tolerância a erros (fuzziness) e filtros compostos, sem carregar o banco
transacional. O Elasticsearch é um **índice de leitura denormalizado** — o **PostgreSQL segue a fonte
de verdade** e o índice é reconstruível a partir dele a qualquer momento.

### 16.1 🧱 As peças

Config compartilhada em `shared/infrastructure/search/`; documentos/repositórios por módulo em
`<módulo>/infrastructure/search/`; serviço em `application/service/`; router em `presentation/router/`:

| Arquivo | Papel |
| :------ | :---- |
| `shared/.../search/elasticsearch_config.py` | `ElasticsearchConfig` — `get_client()` (cliente **síncrono** singleton) + `create_indices(documents)` **idempotente** (recebe as classes do chamador; `shared` não importa módulos de negócio) |
| `shared/.../search/analyzers.py` | `portuguese_analyzer` customizado (lowercase + stopwords + _stemming_ leve), registrado nas settings do índice ao ser referenciado num campo |
| `clients/.../search/client_document.py`, `contracts/.../search/contract_document.py` | `Document` por entidade — `Keyword` (filtro exato), `Text` (analisado PT), `Date`/`Boolean`/`Double`; `from_entity` achata enums/`Decimal`/id (`meta.id`) |
| `clients/.../search/client_search_repository.py`, `contracts/...` | Indexação (`save`/`delete`) + _finders_ estruturados (`term`/`match`/`bool`) |
| `clients/application/service/client_search_service.py` | `search` (`multi_match` + fuzziness), `filter_by_location`, `advanced_search`; paginação via `PageRequest`/`PageResponse` |
| `shared/application/dto/search_filter.py` | `SearchFilter` / `FilterCondition` (`eq` → term, `gt`/`lt`/`gte`/`lte` → range) |
| `clients/presentation/router/client_search_router.py` | Router `/api/v1/search/clients` (GET `/`, GET `/location`, POST `/advanced`) |

Os índices são criados no **`lifespan`** da app (`create_indices([ClientDocument, ContractDocument])`,
guardado). `ClientMapper.document_to_response_dto` projeta o documento de volta no `ClientResponseDTO`.

### 16.2 🔤 `Keyword` vs. `Text` + full-text com boosting

Atributos de casamento exato (cnpj, email, city, state, ids, status/tipo) são `Keyword`; os nomes
(razão social/fantasia) são `Text` com o analisador português. A busca full-text é um único
`multi_match` com **boosting** (`corporate_name^2`, `trade_name^1.5`, `cnpj`) e **`fuzziness='AUTO'`**,
ordenado por relevância:

```python
search = self._repository.new_search().query(
    "multi_match", query=query, fields=["corporate_name^2", "trade_name^1.5", "cnpj"], fuzziness="AUTO"
)
response = search[offset : offset + limit].execute()
total = response.hits.total.value  # -> PageResponse.total_elements
```

### 16.3 🎛️ Busca avançada e `min_score`

`advanced_search` monta uma query `bool` composta: um `multi_match` **opcional** + cada `FilterCondition`
vira um `term` (operador `eq`) ou `range` (`gt`/`lt`/`gte`/`lte`) no _filter context_; um `min_score`
opcional descarta hits de baixa relevância. Espelha o split _finders_ × filtro-DTO da persistência (Fase 5).

### 16.4 ⚠️ Notas e limitações

- **Índice secundário, não autoritativo:** a API `save`/`delete` mantém o índice, mas a **sincronização
  garantida em tempo real** (consumir eventos da Fase 10 para reindexar) fica para uma fase posterior;
  hoje o índice é populado sob demanda e **reconstruível** a partir do Postgres.
- **Síncrono em threadpool:** cliente ES síncrono; serviço/endpoints são `def` → o FastAPI os roda num
  _threadpool_ (não bloqueiam o event loop). Router sob `/api/v1/search/clients` (prefixo próprio para
  não colidir com `/api/v1/clients/{id}`).
- **Deps/tipos:** `elasticsearch ^8.0` (tipado) + `elasticsearch-dsl ^8.0` (sem `py.typed` → _override_
  de mypy `elasticsearch_dsl.*`). Segurança do cluster **desabilitada** (dev/local). No Windows, o ES
  **conecta do host** (como Redis/RabbitMQ/Kafka; só o Postgres falha).
- **Alavancas de _tuning_** (latência, sem mudar o contrato): campos `Keyword` extras para filtros
  frequentes; ajuste do analisador (stopwords/stemming); dimensionamento de _shards_/réplicas.

---

## 📈 17. Observabilidade (Prometheus/Grafana · Fase 12)

A **Fase 12** (versão `0.12.0`) adicionou **observabilidade em tempo real** — o complemento numérico
("o que está acontecendo agora") aos logs. É aditiva e transversal: instrumenta o `main.py`, adiciona
`shared/infrastructure/metrics/`, instrumenta serviços e sobe Prometheus/Grafana/Alertmanager no compose,
**sem** alterar contratos de API existentes.

### 17.1 🧱 As peças

| Arquivo / serviço | Papel |
| :---------------- | :---- |
| `main.py` (instrumentator) | `prometheus-fastapi-instrumentator` → métricas HTTP `fastapi_*` (contagem, latência, in-progress) + endpoint `/metrics` (**excluído** da própria instrumentação) |
| `shared/.../metrics/metrics_config.py` | `MetricsConfig` — coletores customizados como **atributos de classe** (registro único, evita duplicação) + `application_info`; `set_application_info(...)` |
| `shared/.../metrics/business_metrics.py` | `BusinessMetrics` (fachada singleton) + `record_safely` (registro **livre de falhas**) |
| `shared/.../metrics/system_metrics.py` | `SystemMetricsCollector` — gauges de host (memória/CPU/disco) **refrescados no scrape** via `collect()` |
| `prometheus/` | `prometheus.yml` (scrape + rules + alerting), `alerts.yml`, `alertmanager.yml` |
| `grafana/` | provisioning (data source + provider) + dashboards Aplicação/Negócio/Infra |

O `lifespan` faz `set_application_info(...)`, `business_metrics.initialize([status…])` (zero-init das
séries rotuladas; os status vêm do `main`, preservando a regra de dependência) e `register_system_metrics()`.

### 17.2 📊 Catálogo de métricas

- **HTTP (default):** `fastapi_requests_total{handler,method,status}`, `fastapi_request_duration_seconds_*`,
  `fastapi_requests_inprogress`. Nomes `fastapi_*` escolhidos para casar com a PromQL do plano.
- **Negócio:** `client_created_total`, `contract_created_total{status}`, `invoice_paid_total`,
  `clients_active` (gauge), `operation_duration_seconds{endpoint,method}` (histograma).
- **Recursos:** `memory_usage_bytes`, `memory_available_bytes`, `cpu_usage_percent`, `disk_usage_percent`.
- **Info:** `application_info{name,environment,version}`.

Instrumentação nos serviços: `ClientService.create` (duração + `client_created`), `ContractService.create`
(por status) e `InvoiceService.update` (`invoice_paid` ao transitar → PAID) — sempre via `record_safely`,
para que um erro de métrica **nunca** quebre a operação de negócio.

### 17.3 🛰️ Coleta, dashboards e alertas

O app roda **no host** (`uvicorn :8000`); o **Prometheus** (container) o scrapeia via
`host.docker.internal:8000` (`extra_hosts: host-gateway` cobre Linux). O **Grafana** provisiona o data
source Prometheus + 3 dashboards. As regras (`HighRequestLatency` p95>1s, `HighErrorRate` 5xx>5%,
`LowMemory` disponível<500 MB) são avaliadas pelo Prometheus e roteadas ao **Alertmanager**.

### 17.4 ⚠️ Notas e limitações

- **Segurança:** `/metrics` fica **aberto** na rede interna; credenciais do Grafana (`admin`/`admin`) e o
  receiver do Alertmanager são **placeholders** — trocar por _secrets_ antes de qualquer uso não-local.
- **Não-bloqueante:** o registro de métrica é efeito colateral guardado (`record_safely`); métricas de
  recurso usam `psutil` (**sem stubs** → _override_ de mypy `psutil`).
- **Escopo:** apenas métricas + alertas por threshold (sem tracing/OpenTelemetry, sem SLO); host via
  `psutil` in-process (upgrade natural: `node_exporter`). No Windows, a stack **conecta do host**.

---

## 🧪 18. Estratégia de Testes (Fase 13)

A suíte (em `energyhub/tests/`, espelhando a árvore de módulos) roda com **um comando** e aplica um
**_quality gate_ de 80%** embutido no `addopts` do `pyproject.toml` (`--cov=energyhub
--cov-fail-under=80`), de modo que **toda** invocação — local ou CI — enforça o mesmo piso. São **três
camadas**, dos testes mais rápidos/isolados aos mais realistas:

| Camada | O que cobre | Como | Precisa de Docker? |
| :----- | :---------- | :--- | :----------------: |
| **Unitário** | Os 15 serviços de aplicação (regras de negócio) + value objects, validadores, utilitários, paginação, exception handlers, `JwtService`/hashing, métricas | Serviço instanciado com colaboradores `AsyncMock`/`Mock`; caminhos felizes **e** de exceção de domínio | Não |
| **Componente** | Os 13 routers (roteamento, status HTTP, serialização, _guards_ RBAC) | `TestClient` sobre um app mínimo + `dependency_overrides`: `get_current_user` (usuário com todas as permissões) e os provedores de serviço mockados | Não |
| **Integração** | Repositórios contra SQL real + fluxo de API ponta-a-ponta | Repositório sobre `PostgresContainer` (Testcontainers) com isolamento por rollback; API via `TestClient` com **login JWT real** → `POST /clients` → `201` | **Sim** |

**Decisões-chave:**

- **`AsyncMock` para colaboradores async, `Mock` para síncronos** (`pytest-asyncio` em modo `auto`
  coleta `async def test_...` sem marcador por teste). Awaitar um `Mock` comum levantaria erro.
- **Cache em memória por teste.** Os métodos de serviço decorados com `@cache` (fastapi-cache2) e o
  `invalidate_cache` das escritas exigem um backend inicializado; um `conftest.py` inicializa um
  `InMemoryBackend` **novo por teste** (o `_store` é atributo de classe → limpo explicitamente), tornando
  os serviços testáveis sem Redis e sem vazamento de estado entre testes.
- **Override apenas de `get_current_user`.** Como `require_permission(perm)` resolve o usuário atual via
  `get_current_user` e checa `has_permission`, um único override (usuário que concede tudo) destrava tanto
  a dependência de grupo quanto os _guards_ por rota — sem token nem banco.
- **Isolamento e reprodutibilidade.** Testcontainers dá um Postgres real e efêmero (SQL/constraints
  verdadeiros, ao contrário de SQLite); `docker-compose.test.yml` oferece PG/Redis/RabbitMQ em portas
  não-padrão (**5433/6380/5673**) para runs manuais, sem colidir com o ambiente de desenvolvimento.
- **Gate _single-sourced_.** O limiar vive no `addopts` (e em `[tool.coverage.report] fail_under=80`),
  então não há comando separado a lembrar; `main.py`/`__init__.py`/`tests` são omitidos para manter o
  percentual significativo. Para iterar sem o gate: `pytest --no-cov`.

**Execução no Windows.** O Postgres **não** é acessível host→container (peculiaridade do proxy do Docker
Desktop) — os demais serviços conectam do host. Por isso a **camada de integração roda dentro de um
container** na rede do compose (os testes marcados `integration` são **pulados automaticamente** no host
via _skip-guards_), enquanto unitários e componente rodam no host. Resultado verificado: **273 testes
passam no host** (cobertura **85%**, integração pulada) e **279 passam in-container** (cobertura **87%**,
gate satisfeito). A estabilização não revelou defeito de aplicação — só ajustes de _harness_.

---

## 🐳 19. Containerização e Orquestração (Fase 14)

A aplicação é empacotada numa imagem Docker e **toda a stack sobe com um comando**
(`docker compose up -d`). Artefatos na raiz do repositório: `Dockerfile`, `.dockerignore` e o
`docker-compose.yml` (que passou a incluir a própria API, além da infra das Fases 4–12).

**Imagem (`Dockerfile`) — build multi-stage, runtime slim e não-root:**

- **Estágio `builder`** (`python:3.12-slim` + Poetry): resolve **só** as dependências de produção —
  `poetry install --only main --no-root` — num virtualenv em `/app/.venv`. Copiar apenas os
  manifestos (`pyproject.toml`/`poetry.lock`) antes do código aproveita o **cache de camadas**: as
  deps não reinstalam quando só o código muda.
- **Estágio `runtime`** (`python:3.12-slim`): copia **apenas** o `/app/.venv` resolvido + o código
  (`src`, `alembic`) — sem Poetry nem compiladores. Cria o usuário **`appuser`** (não-root), faz
  `chown` do `/app`, `EXPOSE 8000` e `CMD ["uvicorn", "energyhub.main:app", "--host", "0.0.0.0",
  "--port", "8000"]`. O pacote é importado via `PYTHONPATH=/app/src`.
- **Detalhe load-bearing:** o venv é criado **no mesmo caminho** (`/app/.venv`) em ambos os estágios,
  senão os _shebangs_ dos console scripts (uvicorn/alembic) apontariam para o caminho do `builder` e
  o `exec` falharia com _"no such file or directory"_. A versão do Poetry na imagem casa com a do host
  (`2.4.1`) para o `poetry.lock` (formato PEP 735 `[dependency-groups]`) validar.

**Orquestração (`docker-compose.yml`):**

- **Serviço `energyhub-api`** construído pelo `Dockerfile`, publicando `:8000`, `restart:
  unless-stopped`, ao lado de Postgres, Redis, RabbitMQ, Kafka + Zookeeper, Elasticsearch, Prometheus,
  Grafana e Alertmanager — todos na rede _bridge_ **`energyhub-network`** (resolvem-se por nome).
- **Startup health-gated:** a API declara `depends_on: { condition: service_healthy }` para
  Postgres/Redis/RabbitMQ/Elasticsearch/Kafka — só inicia depois de todos saudáveis, eliminando a
  corrida clássica "app sobe antes do banco aceitar conexões". `start_period` no ES/Kafka dá folga
  para a primeira inicialização (evita que checagens antes da prontidão contem como falha).
- **Config 12-factor:** toda a configuração é injetada por variável de ambiente e as URLs endereçam
  as dependências por **nome de serviço** (`postgres`, `redis`, `rabbitmq`, `elasticsearch`,
  `kafka:29092`), **nunca `localhost`** — a mesma imagem roda em qualquer ambiente sem rebuild.
  Nenhum segredo é embutido na imagem.
- **Persistência:** volumes nomeados para cada serviço com estado (`postgres_data`, `redis_data`,
  `rabbitmq_data`, `elasticsearch_data`, `prometheus_data`, `grafana_data`) montados no diretório de
  dados; o Redis roda com **AOF** (`--appendonly yes`). Os dados sobrevivem a `docker compose down`/`up`.
- **Observabilidade na rede:** com a API agora na stack, o `prometheus/prometheus.yml` scrapeia
  **`energyhub-api:8000`** (antes era `host.docker.internal:8000`, quando a app rodava no host).

**Migrações.** A imagem inclui o `alembic`; no primeiro boot com banco vazio, aplique o schema (que
também semeia o `admin`) com `docker compose exec energyhub-api alembic upgrade head`. O `CMD` da
imagem é apenas o uvicorn — migração é passo explícito, não efeito colateral do startup.

**Segurança.** As credenciais dos serviços e o `SECRET_KEY` no compose são **placeholders de
desenvolvimento** — devem ser rotacionados e externalizados (`.env` / secrets manager) antes de
qualquer uso em produção. A API roda como usuário não-root, reduzindo o _blast radius_.

> **Nota de versões (reconciliação):** foram mantidas as versões de imagem já validadas nas Fases
> 10–12 (Elasticsearch `8.13.4`, Kafka/Zookeeper `7.6.1`, Prometheus `v2.54.1`, Grafana `11.2.0`) em
> vez das do plano original (`8.11.0`/`7.5.0`): um _downgrade_ do Elasticsearch quebraria o volume de
> dados existente (índices `8.13.4` não abrem no `8.11.0`) sem qualquer ganho.

---

## 🕸️ 20. Decomposição em Microsserviços (Fase 15)

A Fase 15 divide o monólito modular em **serviços FastAPI independentemente implantáveis** (mudança
**_breaking_**), preservando o comportamento de domínio. É uma mudança de **topologia**: o processo
único vira uma malha de serviços que se comunicam pela rede. A decomposição está documentada em
[`docs/bounded-contexts.md`](./bounded-contexts.md).

**Serviços extraídos** (em `services/<nome>-service/`, cada um dono do seu banco):

| Serviço | Porta | Banco | Upstream (clientes HTTP) |
| :------ | :---: | :---- | :----------------------- |
| `auth-service` | 8001 | `authdb` | — (raiz) |
| `client-service` | 8002 | `clientdb` | `AuthClient` |
| `contract-service` | 8003 | `contractdb` | `AuthClient`, `ClientClient` |
| `financial-service` | 8004 | `financialdb` | `AuthClient`, `ClientClient`, `ContractClient` |
| `audit-service` | 8005 | `auditdb` | — (consome eventos do RabbitMQ) |

**Anatomia de um serviço.** Cada projeto é autocontido (não importa código de irmãos nem do monólito):
`pyproject.toml` + `Dockerfile` (multi-stage, não-root) próprios; `energyhub/config.py` (`Settings`
com `app_name`/`app_port`/Consul/URLs upstream); `energyhub/main.py` (lifespan: mapeia, cria o schema,
registra no Consul, fecha os clientes no shutdown; `/health`); um `mapping.py` **enxuto** que mapeia
**só as tabelas do serviço** — referências cross-context (ex.: `contracts.client_id`) viram **UUID sem
FK**, pois a tabela dona vive noutro serviço/banco. O kernel `shared/` e o módulo de domínio são
**copiados** (extração fiel), não referenciados.

**Service discovery (Consul).** `energyhub/discovery.py::register_with_consul` registra o serviço no
startup (nome lógico + `service_id = {name}-{instance_id}` — `HOSTNAME` do pod, ou `uuid4` por processo
fora do k8s, **único por réplica** — + endereço/porta + **health check HTTP** contra `/health`) e
desregistra a **própria** instância no shutdown — via **API HTTP do Consul** (`httpx`). Callers e o
gateway resolvem dependências por **nome**, não por host/porta fixos.

**Comunicação entre serviços (`httpx`).** Cada dependência upstream tem um cliente dedicado
(`AuthClient`/`ClientClient`/`ContractClient`) sobre uma base comum `ServiceClient`. A substituição
central da chamada in-process é o **`get_current_user`** dos serviços downstream: em vez de ler a
tabela `users` (que não possuem), decodificam o JWT e resolvem o usuário — com papéis/permissões — no
`auth-service` (endpoints internos `/internal/users/...`, não publicados pelo gateway).

**Resiliência (`tenacity`).** `ServiceClient` aplica, em toda chamada: **timeout** explícito; **retry**
com _backoff_ exponencial e tentativas limitadas (3) para falhas transientes; `raise_for_status` para
surfaçar erros de upstream; e um **fallback** (`None`) quando as tentativas se esgotam — a falha de uma
dependência fica **contida** (ex.: vira 401), sem cascatear nem pendurar a requisição. Os pools `httpx`
são fechados no shutdown.

**API Gateway (Traefik).** Ponto de entrada único (`:80`). O provider **Consul-catalog** monta as rotas
a partir das **tags `traefik.*`** que cada serviço publica no Consul, roteando por **prefixo de caminho**
(`/api/v1/auth`→auth, `/api/v1/clients`→client, ...). Middlewares de **borda**: `forwardAuth` →
`auth-service/internal/auth/verify` (autenticação), `accessLog` (logging) e `ratelimit`.

> **Reconciliações (Windows).** Registro no Consul via **API HTTP** (`httpx`) em vez de `python-consul`
> (assíncrono-friendly, uma dependência a menos). Roteamento do Traefik via **Consul-catalog** porque o
> provider **Docker** do Traefik não alcança o daemon do Docker Desktop no Windows (mesma classe de
> peculiaridade do Postgres host→container). O monólito `energyhub-api` **permanece** no compose
> (estratégia _strangler_): serve os contextos ainda não extraídos até que sejam migrados.

---

## ☸️ 21. Orquestração com Kubernetes (Fase 16)

A Fase 16 declara **toda a plataforma como manifestos Kubernetes** em [`k8s/`](../k8s/) — o estado
desejado de um cluster. Desde o endurecimento (_k8s-production-robustness_), os manifestos vivem sob
[`k8s/base/`](../k8s/base/) e são aplicados por **overlays Kustomize** —
`kubectl apply -k k8s/overlays/dev` (ou `prod`), não mais `kubectl apply -f k8s/`. Consome as imagens
da Fase 14 e as fronteiras da Fase 15; **não altera código de aplicação** — só a camada de
orquestração. Validado num cluster **minikube** local (Kubernetes v1.35). Procedimento completo em
[`k8s/README.md`](../k8s/README.md).

**O que roda no cluster** (namespace `energyhub`; a base em [`k8s/base/`](../k8s/base/) renderiza ~54
documentos via `kubectl kustomize k8s/overlays/<env>`):

| Camada | Recursos |
| :----- | :------- |
| Microsserviços | `Deployment` + `Service` (ClusterIP) + `HPA` — auth/client/contract/financial/audit |
| Gateway/discovery | `traefik` + `traefik-service` (**LoadBalancer**), `consul` + `consul-service` |
| Borda | `Ingress` (classe `nginx`) `energyhub.local` → `traefik-service:80`, com **TLS terminado via cert-manager** (Secret `energyhub-tls`, `force-ssl-redirect`) |
| Backends stateful | `postgres` (+ initdb dos 5 bancos), `redis`, `rabbitmq` — todos **PVC-backed**; `kafka` = **StatefulSet KRaft** (sem Zookeeper) |
| Segurança _(pós-`1.0.0`)_ | **NetworkPolicies** _default-deny_ + _allow_ de menor privilégio; `ServiceAccount` `energyhub-sa` + `ghcr-pull-secret` (pull autenticado do GHCR) |
| Config | `energyhub-config` + `<svc>-config` (ConfigMaps) + `energyhub-secret` (resolvido no cluster por SealedSecret/ExternalSecret) |

**Config × Secret.** Valores não sensíveis (ambiente, Consul, porta, `SERVICE_HOST`, Redis/Kafka)
em **ConfigMaps** (injetados por `envFrom` + montados como volume); `SECRET_KEY`, senhas e as
`*_DATABASE_URL`/`RABBITMQ_URL` (que embutem a senha) num **Secret** (`valueFrom.secretKeyRef`). Desde
o endurecimento, o `energyhub-secret` **não é um manifesto em texto puro**: ele é resolvido **dentro
do cluster** por um **SealedSecret** (cifrado) ou **ExternalSecret** (Vault) — ver
[`k8s/secrets/`](../k8s/secrets/README.md). NetworkPolicies _default-deny_ isolam o namespace
(cada serviço só recebe do que precisa), e a borda termina **TLS** via cert-manager.

**Deployments.** `replicas: 2`, `resources.requests/limits` (CPU/memória), `liveness`/`readiness`
contra `/health` (self-healing: readiness porteia o tráfego, liveness recria o pod travado). DNS do
cluster (`consul-service`, `postgres-service`, `client-service`, …) substitui os hostnames do Compose.

**Networking.** `ClusterIP` para o tráfego interno (DNS estável, endpoints só de pods _ready_);
`LoadBalancer` + `Ingress` na borda. O Traefik mantém o provider **Consul-catalog** da Fase 15
(cada serviço publica suas tags `traefik.*` no Consul ao registrar).

**Autoscaling.** Um `HorizontalPodAutoscaler` (`autoscaling/v2`) por serviço — CPU 70% / memória 80%,
`min 2`/`max 5` — alimentado pelo **Metrics Server**. Verificado sob carga: o `auth-service`
escalou **2 → 5** (`SuccessfulRescale … cpu … above target`) e recolheu a `2` após a janela de
estabilização.

**Backends stateful in-cluster (decisão).** Em dev os data stores rodam **dentro** do cluster
(endereçados por DNS). Desde o endurecimento (_k8s-production-robustness_) o armazenamento é
**durável** — cada backend monta um `PersistentVolumeClaim` (Postgres/Redis/RabbitMQ) ou um
`volumeClaimTemplate` (Kafka), não mais `emptyDir` — e o dado sobrevive a restart/reschedule. Em
produção, alternativamente troque para managed stores externos ajustando **só as URLs no Secret**.

> **Correções necessárias sob k8s (reconciliações reais):**
> - **`enableServiceLinks: false`** nos 5 serviços — o k8s injeta env vars estilo docker-links
>   (ex.: `AUTH_SERVICE_PORT=tcp://…:8001`) que colidem com os campos `*_service_port` do `Settings`
>   (pydantic) e quebram o parse. Desligá-las faz o app usar seus defaults de DNS + Consul.
> - **Kafka (modo KRaft, _k8s-production-robustness_)**: roda como `StatefulSet` combinando
>   broker+controller, **sem Zookeeper** — o que aposenta o antigo `strategy: Recreate` (que existia
>   só para dois brokers não disputarem `broker.id` no znode). `KAFKA_HEAP_OPTS=-Xmx512m` (o default
>   `-Xmx1G` estoura o limite → `OOMKilled`); `publishNotReadyAddresses: true` nos Services (o broker
>   precisa alcançar o próprio listener/controller **antes** do readiness); `CLUSTER_ID` é um UUID de
>   16 bytes em base64url (o `kafka-storage format` o exige). Tópicos com `auto-create` off devem ser
>   criados (ex.: `contract-events`).
>
> **Duas limitações herdadas da Fase 15 — ambas CORRIGIDAS em `fix-microservices-gaps` (pós-`1.0.0`):**
> (1) o `service_id` era `{name}-{port}` (não único por réplica), então o shutdown de uma réplica
> desregistrava o ID compartilhado e sumia com o serviço no Consul — agora é `{name}-{instance_id}`
> (`HOSTNAME` do pod/`uuid4`), único por réplica, com _deregister_ da própria instância. (2) A trilha
> de **auditoria** não era auto-populada — hoje um `AuditEventProducer` publica na fila `audit` em
> **todo** create/update/delete dos serviços, e o `AuditConsumer` persiste (também foi corrigido um bug
> pré-existente em que o consumidor nunca ficava assinado). Validado ao vivo (2 réplicas com IDs
> distintos; trilha e2e em `audit_logs`).

**Validação e2e (no cluster).** Login → criar cliente → criar contrato **pelo gateway**
(`ingress → Traefik → Consul-catalog → serviço`, com `forwardAuth` no `auth-service`) retornaram
`200/201/201`; DNS inter-serviço e endpoints confirmados; eventos/logs sem erros novos após as correções.

---

## 🔁 22. Automação CI/CD (GitHub Actions · Fase 17)

A Fase 17 fecha o ciclo: 5 workflows em [`.github/workflows/`](../.github/workflows/) que, a cada
push, **constroem, testam, imageiam, publicam e deployam** com _rollback_. É **configuração** (YAML),
não código de aplicação; consome o projeto Poetry (Fase 1), os testes (Fase 13), os `Dockerfile`s
(Fase 15) e os manifestos `k8s/` (Fase 16). Guia completo em [`ci-cd.md`](./ci-cd.md).

| Workflow | Papel |
| :------- | :---- |
| `build.yml` | `poetry build` + `pytest` (cobertura → Codecov) |
| `test.yml` | Postgres/Redis _service containers_ + **migração Alembic** + unit/integração |
| `docker.yml` | _matrix_ Buildx → 5 imagens no **GHCR** (`latest`+SHA, via `metadata-action`) |
| `deploy.yml` | deploy real (`KUBE_CONFIG`) — `apply` + `rollout status`/`wait` + **rollback** + Slack |
| `ci-cd.yml` | esteira `build-and-test → build-and-push → deploy` (`needs`), deploy validado em **kind efêmero** |

**Decisões-chave.** Registry **GHCR** (grátis, `GITHUB_TOKEN`; Docker Hub/ECR como alternativa por
config); imagens com tag **imutável por SHA** + `latest`; deploy **declarativo via Kustomize** — o SHA
é injetado no `images:` transformer e aplicado com `kubectl apply -k k8s/overlays/prod` (sem
`kubectl set image`; ver §21 e `k8s-production-robustness`) — com **auto-rollback** (`rollout undo`) na
falha do _rollout_; secrets opcionais (`KUBE_CONFIG`/`SLACK_WEBHOOK_URL`/`CODECOV_TOKEN`) fazem o
pipeline **degradar sem quebrar** (o deploy real é pulado sem cluster). A validação _live_ de deploy
roda **grátis num kind efêmero** no runner (aplica `kubectl apply -k k8s/overlays/dev`, aguarda o
subconjunto core e faz um _drill_ de rollback) — sem cluster 24/7. Registro datado da esteira verde ao
vivo em [`pipeline-validation.md`](./pipeline-validation.md).

> **Reconciliações (spec → realidade).** Gateway = **Traefik** (imagem oficial, não construída) → a
> matrix cobre os 5 serviços; **`8398a7/action-slack` arquivado** → `slackapi/slack-github-action@v2`;
> **integração skip-guarded** (não `tests/unit|integration`) → passos distintos por presença do banco;
> **Alembic antes da integração** (o monólito cria o schema por migração, não no boot).

---

## 🚀 23. Como adicionar uma nova entidade/módulo (próximas fases)

Passo a passo curto, aproveitando o esqueleto já existente:

1. **Escolha o módulo** dono da entidade (ex.: `clients`). A árvore de 4 camadas × sub-pacotes já
   está criada — não é preciso recriar diretórios.
2. **Domain** — crie a entidade em `clients/domain/entity/` estendendo `BaseEntity`
   (`@dataclass(kw_only=True)`), com validação no `__post_init__` levantando `ValidationException` e
   relacionamentos como referências Python (`field(compare=False, repr=False)`); declare _value
   objects_ em `valueobject/` (frozen dataclasses), a interface de repositório em `repository/`
   estendendo `Repository[T, ID]`, e exceções específicas em `exception/` (subclassando
   `DomainException` ou uma das 3 filhas). Os módulos já entregues na Fase 3 (ver
   Seção 8) servem de exemplo concreto desses padrões.
3. **Application** — crie DTOs em `dto/` (estendendo `BaseDTO` quando fizer sentido), mapeadores em
   `mapper/`, e casos de uso em `usecase/` implementando `UseCase[Input, Output]`.
4. **Infrastructure** — adicione a `Table` + `registry.map_imperatively(...)` da entidade em
   `shared/infrastructure/persistence/mapping.py` (mantendo o domínio puro) e crie o repositório
   concreto em `<módulo>/infrastructure/persistence/`, estendendo `SQLAlchemyRepository[T, ID]`
   (ver Seção 10).
5. **Presentation** — crie o router em `router/` usando/estendendo `BaseRouter`, os _schemas_ em
   `request/`/`response/`, e registre o router na app (`main.py`). **Proteja-o**: `dependencies=[Depends(get_current_user)]`
   no grupo e `Depends(require_permission(<PERM>))` por endpoint, com a permissão do catálogo (ver Seção 12).
   **Documente-o** (Seção 13): `summary`/`description`/`responses` por rota (compondo os blocos de
   `openapi_responses`), uma `tag` própria, `Field(description/examples)` nos DTOs e um `error_code` em
   cada exceção nova (registrando-o em `docs/API_ERRORS.md`).
6. **Registre o `global_exception_handler`** na app quando começar a expor endpoints de negócio,
   para respostas de erro padronizadas (`ErrorResponse`).
7. **Testes** — adicione testes em `tests/`, seguindo `tests/test_base_entity.py` e a fixture de
   `TestClient` em `conftest.py`.

> 🧭 Regra de ouro: mantenha a **regra de dependência** (Seção 5). Se um bloco apareceria idêntico
> em 2+ módulos, promova-o para `shared` em vez de duplicá-lo.

---

## 📚 24. Referências

- 📐 [Arquitetura planejada (Fase 0)](./fase-0/07-arquitetura.md) — o design de referência: 9
  módulos, 4 camadas, sub-pacotes normativos, agregados e regras de dependência.
- 📖 [README do projeto](../README.md) — visão geral do EnergyHub, stack, estrutura e como começar.
