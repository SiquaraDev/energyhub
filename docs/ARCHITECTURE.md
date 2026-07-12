# ⚡ EnergyHub — Arquitetura Base (as-built · Fase 2)

Este documento descreve a arquitetura **como construída** (_as-built_) do EnergyHub ao final da
**Fase 2 — Clean Architecture e Classes Base** (versão `0.2.0`). Enquanto o
[documento de arquitetura da Fase 0](./fase-0/07-arquitetura.md) define _como o código **deveria**
se organizar_ (arquitetura planejada), este artefato registra _o que **de fato** existe no
repositório_: o esqueleto completo de **9 módulos × 4 camadas**, as **classes-base** já
implementadas em `shared`, suas **assinaturas reais** e como estendê-las nas próximas fases.

> 📌 Tudo o que segue foi verificado lendo o código-fonte real em `energyhub/src/energyhub/`.
> Em caso de divergência entre a arquitetura planejada (Fase 0) e o código, **este documento**
> reflete o estado atual do repositório; a Fase 0 permanece como a intenção de design.

---

## 🏛️ 1. Visão geral

O EnergyHub segue **Clean Architecture** e **Domain-Driven Design (DDD)** sobre a stack
**Python 3.12+ · FastAPI · SQLAlchemy 2.0 async · PostgreSQL 16**. Ao final da Fase 2, o código
Python está organizado assim:

| Dimensão | Valor (as-built) |
| :------- | :--------------- |
| **Layout** | `src` layout — o pacote vive em `energyhub/src/energyhub/` (não é _flat_) |
| **Módulos** | **9**: `shared`, `auth`, `clients`, `contracts`, `negotiations`, `financial`, `audit`, `notifications`, `reports` |
| **Camadas por módulo** | **4**: `domain`, `application`, `infrastructure`, `presentation` |
| **Classes-base** | Concentradas em `shared`, uma para cada bloco fundamental das 4 camadas |
| **App FastAPI** | `src/energyhub/main.py` — expõe `/` e `/health`, com CORS de desenvolvimento |
| **Configuração** | `config/` é **pacote** (não módulo único): `settings.py` + `dependencies/` |

O `shared` é o único módulo **transversal**: não modela negócio, apenas fornece os blocos
reutilizados por todos os demais. Os outros 8 módulos são de **negócio** e, na Fase 2, existem
como esqueleto (árvore de pacotes com `__init__.py`) pronto para receber entidades a partir da
Fase 3.

> 🧱 A anatomia interna é idêntica em todos os módulos: cada um repete as mesmas **4 camadas** e os
> mesmos **sub-pacotes**. Só o `shared` está preenchido com código; os módulos de negócio ainda
> estão vazios (apenas a estrutura de diretórios).

---

## 🗂️ 2. Estrutura de diretórios

Árvore real do pacote (com o `shared` **expandido** e o módulo `auth` como **exemplo** da anatomia
que se repete nos 8 módulos de negócio):

```text
energyhub/                              # projeto Poetry (raiz Python)
├── pyproject.toml   poetry.lock   README.md
├── .env                                # git-ignored (roda a partir de energyhub/)
├── src/energyhub/
│   ├── main.py                         # app FastAPI (/ , /health, CORS)
│   ├── config/                         # pacote de configuração
│   │   ├── __init__.py                 # reexporta Settings, get_settings, settings
│   │   ├── settings.py                 # Settings (pydantic-settings) + get_settings()
│   │   └── dependencies/               # injeção de dependência (vazio até fases futuras)
│   │       └── __init__.py
│   ├── shared/                         # módulo transversal (classes-base)
│   │   ├── domain/
│   │   │   ├── entity/base_entity.py           # BaseEntity
│   │   │   ├── valueobject/                     # (VOs comuns — Fase 3+)
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
│   │   │   ├── persistence/sqlalchemy_repository.py  # SQLAlchemyRepository[T, ID]
│   │   │   ├── messaging/                       # (eventos/mensageria — futuro)
│   │   │   ├── config/                          # (config de infra — futuro)
│   │   │   └── security/                        # (segurança — futuro)
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
│   │   ├── domain/         entity/ valueobject/ repository/ service/ exception/
│   │   ├── application/    dto/ mapper/ usecase/ service/ exception/
│   │   ├── infrastructure/ persistence/ messaging/ config/ security/
│   │   └── presentation/   router/ request/ response/ exception/
│   │
│   ├── clients/  contracts/  negotiations/  financial/           # mesma anatomia de auth/
│   └── audit/    notifications/  reports/                        # mesma anatomia de auth/
│
└── tests/                             # conftest.py (fixture TestClient), test_base_entity.py
```

> ℹ️ Cada pacote e sub-pacote contém um `__init__.py` (são **211** no total). Os diretórios sem
> arquivo `.py` de conteúdo (ex.: `valueobject/`, `mapper/`, `messaging/`) já existem como
> pacotes vazios, prontos para serem preenchidos nas fases seguintes. O `docker-compose.yml`
> (PostgreSQL 16) vive na raiz do repositório, um nível acima de `energyhub/`.

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
| `SQLAlchemyRepository[T, ID]` | `shared/infrastructure/persistence/sqlalchemy_repository.py` | Implementação CRUD assíncrona de `Repository` | `__init__(session: AsyncSession, model_class: type[T])`; CRUD com `commit`/`refresh` |
| `BaseRouter` | `shared/presentation/router/base_router.py` | Encapsula `APIRouter` padronizando prefixo/tags | `__init__(prefix: str = "", tags: list[str] | None = None)`; `get_router() -> APIRouter` |
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

> ⚠️ `SQLAlchemyRepository` assume que `model_class` possui uma coluna `id` e usa
> `# type: ignore[attr-defined]` nos acessos a `.id`. A tipagem será refinada quando a `Base`
> declarativa do ORM existir (Fase 4).

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
> (presentation) importam FastAPI. Verificação da Fase 2: **233 módulos importam sem erro**;
> `ruff`/`mypy`/`black` limpos; `pytest` verde.

---

## 🧰 6. `shared/util`, `shared/constant`, `shared/enums`

Blocos utilitários transversais já preenchidos (exceto `enums`, ainda vazio):

### 6.1 `shared/util/` — funções auxiliares puras

| Arquivo | Funções | Observação |
| :------ | :------ | :--------- |
| `date_utils.py` | `utcnow()`, `to_iso(value)`, `is_past(value)` | Sempre UTC _timezone-aware_ |
| `string_utils.py` | `is_blank(value)`, `normalize_whitespace(value)`, `only_digits(value)` | `only_digits` útil para CNPJ/telefone |
| `validation_utils.py` | `is_valid_email(value)`, `is_valid_cnpj_length(value)`, `is_positive(value)` | Validações básicas — validação rica (ex.: DV do CNPJ) fica nos _Value Objects_ na Fase 3 |

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

## 🚀 8. Como adicionar uma nova entidade/módulo (próximas fases)

Passo a passo curto, aproveitando o esqueleto já existente:

1. **Escolha o módulo** dono da entidade (ex.: `clients`). A árvore de 4 camadas × sub-pacotes já
   está criada — não é preciso recriar diretórios.
2. **Domain** — crie a entidade em `clients/domain/entity/` estendendo `BaseEntity`
   (`@dataclass(kw_only=True)`); declare _value objects_ em `valueobject/`, a interface de
   repositório em `repository/` estendendo `Repository[T, ID]`, e exceções específicas em
   `exception/` (subclassando `DomainException` ou uma das 3 filhas).
3. **Application** — crie DTOs em `dto/` (estendendo `BaseDTO` quando fizer sentido), mapeadores em
   `mapper/`, e casos de uso em `usecase/` implementando `UseCase[Input, Output]`.
4. **Infrastructure** — crie o modelo ORM e o repositório concreto em `persistence/`, estendendo
   `SQLAlchemyRepository[T, ID]`.
5. **Presentation** — crie o router em `router/` usando/estendendo `BaseRouter`, os _schemas_ em
   `request/`/`response/`, e registre o router na app (`main.py`).
6. **Registre o `global_exception_handler`** na app quando começar a expor endpoints de negócio,
   para respostas de erro padronizadas (`ErrorResponse`).
7. **Testes** — adicione testes em `tests/`, seguindo `tests/test_base_entity.py` e a fixture de
   `TestClient` em `conftest.py`.

> 🧭 Regra de ouro: mantenha a **regra de dependência** (Seção 5). Se um bloco apareceria idêntico
> em 2+ módulos, promova-o para `shared` em vez de duplicá-lo.

---

## 📚 9. Referências

- 📐 [Arquitetura planejada (Fase 0)](./fase-0/07-arquitetura.md) — o design de referência: 9
  módulos, 4 camadas, sub-pacotes normativos, agregados e regras de dependência.
- 📖 [README do projeto](../README.md) — visão geral do EnergyHub, stack, estrutura e como começar.
