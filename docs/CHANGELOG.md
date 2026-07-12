# 📜 Changelog

Todas as mudanças relevantes do **EnergyHub** são documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

> **Sobre este changelog.** O EnergyHub está em desenvolvimento e **ainda não possui um
> _release_ estável**. As entradas de versão abaixo (`0.0.0` → `1.0.0`) representam os
> **marcos do projeto**, cada um correspondendo a uma das 18 fases especificadas em
> [`openspec/changes/`](../openspec/changes/) e detalhadas no [ROADMAP](./ROADMAP.md).
> As **Fases 0–5** (`0.0.0` → `0.5.0`) já foram **✅ implementadas e validadas**; as
> versões **`0.6.0` em diante** seguem marcadas como **🔮 Planejado** e sem data definida
> até serem implementadas e validadas.

Categorias utilizadas: **Adicionado** (novas funcionalidades), **Alterado** (mudanças em
funcionalidades existentes), **Corrigido** (correções), **Removido**, **Descontinuado** e
**Segurança**.

---

## [Não lançado]

Estado atual do repositório (fora dos marcos versionados abaixo):

### Adicionado
- Especificações OpenSpec completas para as **18 fases** do projeto (`fase-0` a `fase-17`), cada uma com `proposal.md`, `design.md`, `tasks.md` e _specs_ de capacidades. Baseline OpenSpec (`openspec/specs/`) com **38 capacidades** (7 da Fase 0 + 7 da Fase 2 + 12 da Fase 3 + 5 da Fase 4 + 7 da Fase 5).
- Aplicação FastAPI (`energyhub.main:app`) com endpoints `/` e `/health` e CORS de desenvolvimento, sobre layout `src` (`src/energyhub/`).
- **Esqueleto Clean Architecture já implementado e validado**: 9 módulos × 4 camadas (**211 `__init__.py`**) e as **classes-base compartilhadas** (`BaseEntity`, `Repository`, hierarquia `DomainException`, `BaseDTO`, `UseCase`, `SQLAlchemyRepository`, `BaseRouter`, _exception handler_ global, `ErrorResponse`) — não é mais apenas _scaffolding_.
- **Schema PostgreSQL versionado (Fase 4):** ambiente Alembic (`alembic/`, `alembic.ini`, `env.py`), `Base` declarativa (`shared/infrastructure/persistence/database.py`), 8 migrações (15 tabelas, 42 índices, 4 CHECK, 13 triggers `updated_at`) e _seed_ do admin; marcador `py.typed` no pacote.
- **Camada de persistência (Fase 5):** engine async + `get_session()`, **mapeamento imperativo** das 13 entidades (domínio segue puro), `SQLAlchemyRepository[T, ID]` + 13 repositórios concretos, filtros/DTOs de filtro e paginação (`PageRequest`/`PageResponse`), com testes de integração contra o Postgres do Docker.
- Configuração do Poetry (`pyproject.toml`, formato PEP 621) com FastAPI, Uvicorn, SQLAlchemy 2.0 e asyncpg, além das ferramentas de qualidade (black, isort, flake8, mypy, ruff).
- Licença MIT e documentação de projeto (`README.md`, `ROADMAP.md`, este `CHANGELOG.md`).

---

## [1.0.0] — 🔮 Planejado · _Fase 17 · CI/CD_

Automação completa de build, testes, publicação de imagens e _deploy_ em Kubernetes —
a plataforma torna-se **continuamente entregue e pronta para produção**.

### Adicionado
- Workflow de _build_ (`.github/workflows/build.yml`): checkout, Python 3.12 + Poetry, `poetry build`, testes e envio de relatório de cobertura.
- Workflow de testes (`.github/workflows/test.yml`) com _service containers_ Postgres e Redis (com _healthchecks_) rodando as suítes unitária e de integração.
- Workflow Docker (`.github/workflows/docker.yml`): _build_ de uma imagem por serviço via _matrix_ Buildx com cache de camadas no registry.
- Publicação de imagens em _container registry_ (Docker Hub ou AWS ECR), com tags `:latest` e `:SHA`.
- Workflow de _deploy_ (`.github/workflows/deploy.yml`): configura `kubectl` a partir do _secret_ `KUBE_CONFIG`, aplica `k8s/` e verifica o _rollout_.
- _Rollback_ automático (`kubectl rollout undo`) com notificação de falha no Slack.
- Orquestrador ponta-a-ponta (`ci-cd.yml`) encadeando build/testes → publicação → deploy, documentado em `docs/ci-cd.md`.

### Segurança
- Credenciais (registry, `KUBE_CONFIG`, webhook Slack) armazenadas como _GitHub Secrets_.

---

## [0.16.0] — 🔮 Planejado · _Fase 16 · Kubernetes_

Toda a topologia declarada como manifestos Kubernetes: serviços distribuídos,
auto-recuperáveis, com autoscaling e um único ponto de entrada externo.

### Adicionado
- Árvore de manifestos `k8s/` com `Namespace` `energyhub` e um conjunto por serviço (auth, client, contract, financial, audit) + componentes de plataforma (Consul, gateway).
- Um `Deployment` por serviço com réplicas, _requests/limits_ e _probes_ de _liveness/readiness_ em `/health`.
- `ConfigMaps` (configuração não sensível) e `Secrets` (senha do banco/RabbitMQ, `SECRET_KEY`/JWT), injetados via `valueFrom` e volumes.
- `Service` por workload — `ClusterIP` para DNS interno e `LoadBalancer` para a borda.
- `Ingress` + _ingress controller_ roteando tráfego externo por host/path até o _gateway_.
- `HorizontalPodAutoscaler` (autoscaling/v2) por serviço, com alvos de CPU (~70%) e memória (~80%) e limites de réplicas (2–5), via _Metrics Server_.

---

## [0.15.0] — 🔮 Planejado · _Fase 15 · Microsserviços_

Decomposição do monólito modular em serviços FastAPI independentemente implantáveis.

### Adicionado
- Documentação dos _bounded contexts_ e do grafo de dependências (`docs/bounded-contexts.md`).
- Extração de **Auth, Clients, Contracts, Financial e Audit** em projetos `services/<nome>-service/` independentes (pyproject, config, banco, Dockerfile e `/health` próprios).
- _Service discovery_ via **Consul** (auto-registro com _health check_ e resolução por nome lógico).
- Comunicação síncrona entre serviços via clientes **httpx** (`AuthClient`, `ClientClient`, `ContractClient`).
- Políticas de resiliência com **tenacity** (timeouts, _retries_ com _backoff_ exponencial e _fallbacks_).
- API Gateway **Traefik** roteando por prefixo de path via catálogo do Consul, com autenticação/logging/_rate limiting_ na borda.

### Alterado
- **⚠️ BREAKING:** o ponto de entrada HTTP único é substituído por pontos de entrada por serviço acessados através do _gateway_; chamadas entre módulos passam a ser chamadas de rede e **cada serviço passa a ter o próprio banco de dados** (sem tabelas compartilhadas).

---

## [0.14.0] — 🔮 Planejado · _Fase 14 · Containerização_

Aplicação empacotada em imagem Docker _slim_ e _non-root_, com a stack completa
orquestrada por Docker Compose (boot com um único comando).

### Adicionado
- `Dockerfile` _multi-stage_ (estágio de _build_ com Poetry + estágio de runtime `python:3.12-slim` como `appuser`, expondo a porta 8000) e `.dockerignore`.
- `docker-compose.yml` definindo `energyhub-api` + PostgreSQL, Redis, RabbitMQ, Elasticsearch, Kafka + Zookeeper, Prometheus e Grafana em uma rede _bridge_ com `restart: unless-stopped`.
- Configuração 12-factor via variáveis de ambiente (`DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `SECRET_KEY`, ...).
- Inicialização condicionada à prontidão das dependências (`depends_on` + _healthchecks_).
- Volumes nomeados para todos os serviços com estado (dados sobrevivem à recriação dos containers).

---

## [0.13.0] — 🔮 Planejado · _Fase 13 · Testes & Cobertura_

Suíte de testes determinística (unitários + integração) com _quality gate_ de **80% de cobertura**.

### Adicionado
- Ferramentas de teste (`pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, `testcontainers`) e configuração `[tool.pytest.ini_options]`.
- Testes unitários dos serviços da camada de aplicação com colaboradores _mockados_ (caminhos felizes e de exceção de domínio).
- Fixtures e _test doubles_ compartilhados em `conftest.py`.
- Testes de integração: repositórios contra `PostgresContainer` (Testcontainers) e API via `TestClient` com login/JWT reais.
- `docker-compose.test.yml` (PostgreSQL, Redis e RabbitMQ em portas não padrão 5433/6380/5673).
- _Quality gate_ de cobertura (`fail_under=80`, `--cov-fail-under=80`) com relatórios HTML e de terminal.

---

## [0.12.0] — 🔮 Planejado · _Fase 12 · Observabilidade_

Visibilidade em tempo real com métricas, dashboards e alertas.

### Adicionado
- Instrumentação Prometheus da app (`/metrics` via `prometheus-fastapi-instrumentator`) com métricas HTTP padrão e `application_info`.
- `MetricsConfig` + `BusinessMetrics` para _counters/gauges/histograms_ customizados (clientes criados, contratos por status, faturas pagas, ...).
- Métricas de recursos do host (memória, CPU, disco) via `psutil`.
- Servidor Prometheus (com `prometheus.yml` e volume) e Grafana com _data source_ e dashboards de aplicação/negócio/infraestrutura.
- Regras de alerta (`alerts.yml`) e Alertmanager (latência alta, taxa de erro alta, recursos baixos).

---

## [0.11.0] — 🔮 Planejado · _Fase 11 · Busca (Elasticsearch)_

Subsistema de busca _full-text_ com relevância, tolerância a erros e filtros compostos.

### Adicionado
- Serviço Elasticsearch single-node (segurança desabilitada, _healthcheck_, volume) e dependências `elasticsearch` / `elasticsearch-dsl`.
- `ElasticsearchConfig` (client factory + _bootstrap_ idempotente de índices) e _settings_ dedicadas.
- Mapeamentos `Document` por entidade (`ClientDocument`, `ContractDocument`) com analisador Português e projeção `from_entity`.
- Repositórios de busca (index/delete/finders) mantendo o Elasticsearch sincronizado com o PostgreSQL.
- `ClientSearchService` com `multi_match` (boost de campos + `fuzziness='AUTO'`), filtros avançados (`SearchFilter`/`FilterCondition`) e endpoints de busca paginados.
- Testes de performance com orçamentos de latência.

---

## [0.10.0] — 🔮 Planejado · _Fase 10 · Mensageria (RabbitMQ & Kafka)_

Comunicação orientada a eventos entre módulos, fora do caminho da requisição.

### Adicionado
- Broker **RabbitMQ** (UI de gerência, _healthcheck_, volume) + `aio-pika` e `RabbitMQConfig` com declaração idempotente de filas duráveis.
- `EventProducer` genérico e _producers_ por módulo publicando eventos após mudanças de estado bem-sucedidas.
- Consumidores assíncronos: `NotificationConsumer` e `AuditConsumer` (ack manual, `prefetch_count=1`).
- **Kafka** + Zookeeper + `aiokafka`, com criação idempotente de _topics_ e `KafkaEventProducer`/`KafkaEventConsumer` (JSON com chave, _consumer groups_).
- Garantias de entrega _at-least-once_, mensagens duráveis/persistentes e `MessagePublishingException` para falhas de publicação isoladas da transação.

---

## [0.9.0] — 🔮 Planejado · _Fase 9 · Cache (Redis)_

_Read-cache_ Redis com invalidação explícita na escrita.

### Adicionado
- Serviço `redis:7-alpine` (`--appendonly yes`, volume, _healthcheck_) e dependências `redis` / `fastapi-cache2[redis]`.
- `CacheConfig` inicializando `FastAPICache` com `RedisBackend`, prefixo `energyhub` e _key builder_ determinístico.
- Cache de métodos de leitura via `@cache` com _namespaces_ por domínio e TTLs escalonados (`CacheConstants`).
- Helpers de invalidação (`invalidate_cache`, `invalidate_all_cache`) acionados em create/update/delete.
- Rota administrativa `/api/v1/cache` (`GET /stats`, `POST /clear`) protegida pela permissão `CACHE_MANAGE`.

---

## [0.8.0] — 🔮 Planejado · _Fase 8 · Documentação da API_

API auto-descritiva com contrato OpenAPI curado e erros padronizados.

### Adicionado
- OpenAPI customizado (`custom_openapi()`) com título/descrição/versão, metadados de contato/licença e _security scheme_ global `bearerAuth`; `/docs`, `/redoc` e `/openapi.json` expostos.
- Documentação por endpoint (summary, description, respostas por status) e agrupamento por _tags_.
- DTOs Pydantic enriquecidos com descrições, _constraints_ e exemplos.
- Esquemas de erro padronizados (`ErrorResponse`, `ValidationErrorResponse`/`FieldError`).
- Atributo `error_code` nas exceções de domínio e catálogo `docs/API_ERRORS.md`.
- Guia `docs/API_EXAMPLES.md` com exemplos `curl` dos fluxos principais.

---

## [0.7.0] — 🔮 Planejado · _Fase 7 · Autenticação & RBAC_

Identidade verificada por JWT e acesso controlado por papéis/permissões.

### Adicionado
- Módulo compartilhado de hashing BCrypt (`get_password_hash`, `verify_password`).
- Configurações JWT e `JwtService` (python-jose, HS256) que cria, decodifica, valida e extrai o _subject_ dos tokens.
- Fluxo de login (`LoginRequestDTO`/`LoginResponseDTO`, `AuthenticationService`, `AuthRouter` — `POST /api/v1/auth/login`).
- Dependência `get_current_user` + `UserDetails` (papéis e permissões achatadas); 401 em token inválido/ausente.
- `require_permission` / `require_role` para RBAC (403 em grant insuficiente).
- `RoleService` e `PermissionService` (somente leitura) e proteção por endpoint (rotas públicas × protegidas).

### Segurança
- JWT stateless (HS256) para escalabilidade horizontal sem sessão compartilhada.
- ⚠️ `SECRET_KEY` padrão e credenciais `admin/admin123` semeadas **devem ser rotacionadas antes de produção**.

---

## [0.6.0] — 🔮 Planejado · _Fase 6 · REST API_

Entidades persistidas expostas como uma API REST documentada.

### Adicionado
- DTOs de request/response Pydantic por módulo (auth, clients, contracts, negotiations, financial) com _constraints_ e metadados OpenAPI.
- Validadores reutilizáveis (ex.: `CnpjValidator`) e _mappers_ entidade ↔ DTO por módulo.
- Hierarquia de exceções de domínio (não-encontrado / já-existe / estado-inválido) mapeada para HTTP 404/409/422.
- Serviços de aplicação (regras de negócio, hashing de senha, resolução de papéis) sobre os repositórios da Fase 5.
- Use cases (`UseCase[Input, Output]`) e routers REST (CRUD + listagem paginada) registrados em `main:app`.
- Documentação Swagger (`/docs`) e ReDoc (`/redoc`).

---

## [0.5.0] — 2026-07-12 · ✅ Lançado · _Fase 5 · Persistência_

Camada de acesso a dados async, tipada e testável sobre o schema da Fase 4.

### Adicionado
- Configuração async do banco em `shared/infrastructure/persistence/database.py` (engine `asyncpg`, `async_sessionmaker` com `expire_on_commit=False`, dependência `get_session()`).
- **Mapeamento imperativo** (`registry.map_imperatively`) das 13 entidades às tabelas da Fase 4 em `mapping.py` — as entidades permanecem _dataclasses_ **puras** (sem SQLAlchemy no domínio); `configure_mappings()` resolve/valida os mappers no _startup_.
- `SQLAlchemyRepository[T, ID]` genérico (`save` faz _flush_, não _commit_; `find_by_id`/`find_all`/`delete_by_id`/`exists_by_id`, além de `find_by`/`find_page`) e **13 repositórios** concretos com _finders_ (`find_by_username`, `find_by_cnpj`, `search_by_name`, …).
- Filtros componíveis (`ClientFilter`, `ContractFilter`) e DTOs de filtro Pydantic (`ClientFilterDTO`, `ContractFilterDTO`); paginação genérica `PageRequest`/`PageResponse` (zero-based, `size` limitado a `MAX_PAGE_SIZE`).
- Testes de integração (CRUD, _finder_, filtro e paginação) contra o Postgres do Docker, com isolamento por _rollback_.

### Alterado
- `BaseEntity` passou a usar **igualdade por identidade** (`eq=False` + `__eq__`/`__hash__` por `id`) — semântica correta de _entidade_ em DDD e requisito para o mapeamento ORM (instâncias hasheáveis).
- `SQLAlchemyRepository.save` deixou de fazer `commit`/`refresh` (Fase 2) e passou a fazer apenas `add` + `flush`, delegando a fronteira transacional ao _use case_ (Fase 6).
- _Override_ de `mypy` escopado à camada de persistência (`*.infrastructure.persistence.*`): o mapeamento imperativo torna a instrumentação do SQLAlchemy invisível ao mypy, gerando falsos positivos nas queries; o restante do código segue sob mypy estrito.

---

## [0.4.0] — 2026-07-12 · ✅ Lançado · _Fase 4 · Schema & Migrações_

Schema PostgreSQL versionado, reproduzível e reversível via Alembic.

### Adicionado
- Ambiente Alembic (`alembic.ini`, `alembic/env.py`, `script.py.mako`, `versions/`) ligado às _settings_ (`database_url`) e ao `Base.metadata`, com nomes de arquivo UTC-timestamped e suporte **online** (asyncpg + `NullPool`) e **offline** (SQL com `literal_binds`).
- `Base` declarativa em `shared/infrastructure/persistence/database.py` e marcador `py.typed` (pacote tipado, PEP 561).
- **8 migrações encadeadas** (`0001`→`0008`) criando as **15 tabelas** do domínio (`users`, `roles`, `permissions`, `user_roles`, `role_permissions`, `clients`, `contacts`, `contracts`, `negotiations`, `energy_transactions`, `invoices`, `payments`, `audit_logs`, `notifications`, `reports`) — PKs UUID via `gen_random_uuid()`, colunas `Numeric` para valores monetários, timestamps e FKs com `ON DELETE` CASCADE (filhos) ou RESTRICT (registros protegidos).
- **42 índices**: simples nos campos de _lookup_/FK; compostos em `contracts(client_id, status)` e `contracts(start_date, end_date)`; temporais em `audit_logs.created_at` e `notifications.created_at`.
- **4 CHECK constraints** (formato de e-mail e CNPJ, `end_date > start_date`, valores de contrato positivos) e a função compartilhada `update_updated_at_column()` com **13 triggers** de `updated_at`.
- _Seed_ idempotente: papéis `ADMIN`/`OPERATOR`/`CLIENT`, 4 permissões base, grants do ADMIN e usuário `admin` (UUIDs fixos, hash bcrypt).
- Extensão `pgcrypto` garantida na primeira migração.

### Alterado
- Domínio `Contract` **endurecido** para alinhar com os CHECKs do banco: `end_date` deve ser **posterior** a `start_date` e `energy_amount`/`unit_price`/`total_value` devem ser **estritamente positivos** (antes permitia igualdade/zero).

### Segurança
- ⚠️ O usuário `admin` semeado usa a senha de _bootstrap_ `ChangeMe123!` (hash bcrypt) — **deve ser rotacionada antes de qualquer uso real**. O _seed_ é reversível.

---

## [0.3.0] — 2026-07-12 · ✅ Lançado · _Fase 3 · Modelo de Domínio_

Camada de domínio DDD completa e independente de infraestrutura.

### Adicionado
- Entidades: `User`/`Role`/`Permission`, `Client`/`Contact`, `Contract`, `Negotiation`/`EnergyTransaction`, `Invoice`/`Payment`, `AuditLog`, `Notification`, `Report`.
- Enums de estado/tipo (`ContractStatus`, `ContractType`, `NegotiationStatus`, `TransactionType`, `InvoiceStatus`, `NotificationStatus`, `AuditAction`, `ContactType`) como `(str, Enum)`.
- _Value Objects_ (`CNPJ`, `Email`, `Money`, `PhoneNumber`, `Address`, `Percentage`) como _frozen dataclasses_ com validação.
- Agregados (`AuthAggregate`, `ClientAggregate`, `ContractAggregate`, `NegotiationAggregate`, `FinancialAggregate`).
- Validações no `__post_init__` (`ValidationException`), métodos de transição de estado (ex.: `Contract.approve/activate`) e exceções de domínio específicas (`InvalidContractStatus/ClientState/Negotiation`).
- Relacionamentos como **referências Python** (listas + refs opcionais) combinados com os agregados — sem ORM nesta fase (mapeamento SQLAlchemy fica na Fase 5).

---

## [0.2.0] — 2026-07-12 · ✅ Lançado · _Fase 2 · Clean Architecture_

Esqueleto de módulos e classes base compartilhadas.

### Adicionado
- Estrutura de **9 módulos** (`shared`, `auth`, `clients`, `contracts`, `negotiations`, `financial`, `audit`, `notifications`, `reports`) × **4 camadas** (domínio, aplicação, infraestrutura, apresentação), com sub-pacotes — **211 `__init__.py`**.
- Classes base de domínio (`BaseEntity`, interface `Repository`, hierarquia `DomainException`: `ResourceNotFound`, `Validation`, `BusinessRule`).
- Classes base de aplicação (`BaseDTO`, `UseCase`, `ApplicationException`).
- Classe base de infraestrutura (`SQLAlchemyRepository` com CRUD async).
- Classes base de apresentação (`BaseRouter`, _exception handler_ global, `ErrorResponse`).
- Módulo `shared` (`util`, `constant`, `enums`) e `config` promovido a **pacote** (`settings.py` + reexport `Settings/get_settings/settings`), com `config/dependencies/` para injeção de dependência e CORS de desenvolvimento em `main.py`.

### Corrigido
- **Revisão adversarial:** `BaseEntity` passou a usar `@dataclass(kw_only=True)` (sem isso, subclasses com campos obrigatórios quebrariam) e ganhou o teste de regressão `tests/test_base_entity.py`.

### Alterado
- `ruff` configurado para **ignorar N818** (o projeto usa nomes `*Exception` para as exceções).

---

## [0.1.0] — 2026-07-12 · ✅ Lançado · _Fase 1 · Scaffolding_

Ambiente de desenvolvimento, tooling e conectividade com o banco.

### Adicionado
- Repositório Git com `.gitignore` abrangente (Python/IDE/OS/Docker/env) e `poetry.lock` versionado.
- Estrutura do projeto FastAPI no formato **PEP 621 `[project]`** + `[dependency-groups]` (Poetry 2.x), Python **3.12+**, sobre **layout `src`** (`src/energyhub/`).
- Dependências principais (FastAPI, SQLAlchemy 2.0 async, Pydantic, asyncpg, Alembic, python-jose, passlib) e ferramentas de qualidade (pytest, black, isort, flake8, mypy, ruff, além de `httpx` para o `TestClient` do Starlette).
- `docker-compose.yml` com PostgreSQL 16.
- Configurações _type-safe_ via `pydantic-settings`.
- Aplicação FastAPI básica com endpoints raiz e `/health`.

---

## [0.0.0] — 2026-07-11 · ✅ Lançado · _Fase 0 · Planejamento_

Fundação de documentação — **sem código** (apenas artefatos de design).

### Adicionado
- Documentação de escopo do sistema (funcionalidades, tipos de usuário, módulos, regras de negócio).
- Requisitos funcionais e não-funcionais (< 200 ms, 10k usuários, 99,9% de _uptime_, segurança, auditabilidade, i18n).
- Casos de uso **UC-01 a UC-11** e diagrama de casos de uso.
- Diagrama Entidade-Relacionamento (DER) completo.
- Diagramas UML (Classe, Sequência, Componentes).
- Catálogo de eventos de negócio (payload, gatilho, consumidores).
- Planejamento de arquitetura em Clean Architecture (módulos e regras de dependência).

---

[Não lançado]: https://github.com/Matheus-Siquara/energyhub/compare/main...HEAD
