# ⚡ EnergyHub — Arquitetura Base (as-built · Fases 2–10)

Este documento descreve a arquitetura **como construída** (_as-built_) do EnergyHub ao final das
**Fases 2 a 10 — Clean Architecture, Classes Base, Modelo de Domínio (DDD), Schema do Banco,
Persistência, API REST, Segurança (JWT/RBAC), Documentação/Erros da API, Cache Redis e Mensageria
(RabbitMQ & Kafka)** (versão `0.10.0`). Enquanto o [documento de arquitetura da Fase 0](./fase-0/07-arquitetura.md)
define _como o código **deveria** se organizar_ (arquitetura planejada), este artefato registra _o que
**de fato** existe no repositório_: o esqueleto completo de **9 módulos × 4 camadas**, as
**classes-base** já implementadas em `shared`, o **modelo de domínio** (entidades, _value objects_,
enums e agregados) das Fases 2–3, o **schema PostgreSQL + migrações Alembic** da Fase 4, a **camada de
persistência** (ORM async + repositórios) da Fase 5, a **API REST** (DTOs, serviços, use cases e
routers) da Fase 6, a **camada de segurança** (login JWT, `get_current_user`, RBAC por permissão) da
Fase 7, a **documentação da API** (OpenAPI curado + erros padronizados) da Fase 8, o **cache Redis**
(fastapi-cache2 + invalidação) da Fase 9, a **camada de mensageria assíncrona** (produtores/consumidores
RabbitMQ + Kafka) da Fase 10, suas **assinaturas reais** e como estendê-las nas próximas fases.

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

## 🚀 16. Como adicionar uma nova entidade/módulo (próximas fases)

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

## 📚 17. Referências

- 📐 [Arquitetura planejada (Fase 0)](./fase-0/07-arquitetura.md) — o design de referência: 9
  módulos, 4 camadas, sub-pacotes normativos, agregados e regras de dependência.
- 📖 [README do projeto](../README.md) — visão geral do EnergyHub, stack, estrutura e como começar.
