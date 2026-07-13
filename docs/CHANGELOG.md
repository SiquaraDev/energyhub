# 📜 Changelog

Todas as mudanças relevantes do **EnergyHub** são documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

> **Sobre este changelog.** O EnergyHub está em desenvolvimento e **ainda não possui um
> _release_ estável**. As entradas de versão abaixo (`0.0.0` → `1.0.0`) representam os
> **marcos do projeto**, cada um correspondendo a uma das 18 fases especificadas em
> [`openspec/changes/`](../openspec/changes/) e detalhadas no [ROADMAP](./ROADMAP.md).
> As **Fases 0–16** (`0.0.0` → `0.16.0`) já foram **✅ implementadas e validadas**; a
> versão **`1.0.0`** (Fase 17) segue marcada como **🔮 Planejado** e sem data definida
> até ser implementada e validada.

Categorias utilizadas: **Adicionado** (novas funcionalidades), **Alterado** (mudanças em
funcionalidades existentes), **Corrigido** (correções), **Removido**, **Descontinuado** e
**Segurança**.

---

## [Não lançado]

Estado atual do repositório (fora dos marcos versionados abaixo):

### Adicionado
- Especificações OpenSpec completas para as **18 fases** do projeto (`fase-0` a `fase-17`), cada uma com `proposal.md`, `design.md`, `tasks.md` e _specs_ de capacidades. Baseline OpenSpec (`openspec/specs/`) com **108 capacidades** (7 da Fase 0 + 7 da Fase 2 + 12 da Fase 3 + 5 da Fase 4 + 7 da Fase 5 + 7 da Fase 6 + 7 da Fase 7 + 6 da Fase 8 + 5 da Fase 9 + 6 da Fase 10 + 7 da Fase 11 + 6 da Fase 12 + 7 da Fase 13 + 7 da Fase 14 + 6 da Fase 15 + 6 da Fase 16).
- Aplicação FastAPI (`energyhub.main:app`) com endpoints `/` e `/health` e CORS de desenvolvimento, sobre layout `src` (`src/energyhub/`).
- **Esqueleto Clean Architecture já implementado e validado**: 9 módulos × 4 camadas (**211 `__init__.py`**) e as **classes-base compartilhadas** (`BaseEntity`, `Repository`, hierarquia `DomainException`, `BaseDTO`, `UseCase`, `SQLAlchemyRepository`, `BaseRouter`, _exception handler_ global, `ErrorResponse`) — não é mais apenas _scaffolding_.
- **Schema PostgreSQL versionado (Fase 4):** ambiente Alembic (`alembic/`, `alembic.ini`, `env.py`), `Base` declarativa (`shared/infrastructure/persistence/database.py`), 8 migrações (15 tabelas, 42 índices, 4 CHECK, 13 triggers `updated_at`) e _seed_ do admin; marcador `py.typed` no pacote.
- **Camada de persistência (Fase 5):** engine async + `get_session()`, **mapeamento imperativo** das 13 entidades (domínio segue puro), `SQLAlchemyRepository[T, ID]` + 13 repositórios concretos, filtros/DTOs de filtro e paginação (`PageRequest`/`PageResponse`), com testes de integração contra o Postgres do Docker.
- **API REST (Fase 6):** camadas de aplicação e apresentação — DTOs/mappers/services/use-cases/exceções e **10 routers (25 endpoints)** sob `/api/v1/`, auto-documentados em `/docs`; handler de exceções domínio→HTTP; `auth` com M2M e hash bcrypt.
- **Segurança JWT/RBAC (Fase 7):** login (`POST /api/v1/auth/login`) + `JwtService` (HS256), `get_current_user`/`UserDetails` e guards `require_permission`/`require_role`; **10 routers protegidos** (54 guards por endpoint), catálogo de permissões (`shared/constant/permissions.py`) e migração `0009` que semeia **38 permissões** e concede todas ao `ADMIN`. Sem token → 401; sem permissão → 403.
- **Documentação da API (Fase 8):** OpenAPI curado (`custom_openapi()` com contato/licença, esquema `bearerAuth` JWT, 12 tags), endpoints e DTOs documentados com exemplos, erros padronizados (`ErrorResponse`/`ValidationErrorResponse` + `error_code`) e guias `docs/API_ERRORS.md` / `docs/API_EXAMPLES.md`.
- **Cache Redis (Fase 9):** serviço `redis:7-alpine` no compose, `CacheConfig`/`CacheConstants`, `@cache` nos reads de 5 serviços (namespaces + TTLs), invalidação em create/update/delete, e router `/api/v1/cache` (`/stats`, `/clear`) protegido por `CACHE_MANAGE` (migração `0010`).
- **Mensageria assíncrona (Fase 10):** brokers **RabbitMQ** (workflows) e **Kafka** + Zookeeper (streams) no compose; `RabbitMQConfig`/`setup_queues` (11 filas duráveis) e `KafkaConfig`/`create_topics` (4 tópicos); `EventProducer` base + `UserEventProducer`/`ClientEventProducer` (RabbitMQ) e `KafkaEventProducer`/`KafkaEventConsumer` (JSON com chave); consumidores `NotificationConsumer` e `AuditConsumer` (ack manual, `prefetch_count=1`); publicação pós-commit nos serviços (não-bloqueante) e `MessagePublishingException`.
- **Busca full-text (Fase 11):** serviço **Elasticsearch** (single-node, healthcheck, volume) no compose + deps `elasticsearch`/`elasticsearch-dsl`; `ElasticsearchConfig` (client factory + `create_indices` idempotente); documentos `ClientDocument`/`ContractDocument` (keyword/text, analisador português, `from_entity`); repositórios de busca (index/delete/finders); `ClientSearchService` (`multi_match` com boosting + `fuzziness='AUTO'`, filtro por localização, busca avançada com `SearchFilter`/`FilterCondition` + `min_score`); router `/api/v1/search/clients` (full-text, location, advanced).
- **Observabilidade (Fase 12):** instrumentação Prometheus (`/metrics` via `prometheus-fastapi-instrumentator`, métricas HTTP `fastapi_*` + `application_info`); `MetricsConfig`/`BusinessMetrics` (`client_created_total`, `contract_created_total{status}`, `invoice_paid_total`, `clients_active`, `operation_duration_seconds`) com serviços instrumentados; recursos do host via `psutil`; stack Prometheus + Grafana (data source + 3 dashboards) + Alertmanager (regras de latência/erro/memória) no compose.
- **Suíte de testes e gate de cobertura (Fase 13):** toolchain `pytest`/`pytest-asyncio`/`pytest-mock`/`pytest-cov`/`testcontainers` (grupo `dev`) e `[tool.pytest.ini_options]` com gate embutido (`--cov=energyhub --cov-fail-under=80`); testes unitários dos 15 serviços com colaboradores `AsyncMock`, testes de componente dos 13 routers via `TestClient`, e integração (repositórios via `PostgresContainer` + API via `TestClient` com JWT real); `docker-compose.test.yml` (PG/Redis/RabbitMQ em 5433/6380/5673); cobertura **87% in-container** (85% no host, com a integração pulada).
- **Containerização e orquestração (Fase 14):** `Dockerfile` multi-stage (build com Poetry `--only main` → runtime `python:3.12-slim`, não-root `appuser`, `EXPOSE 8000`, `CMD uvicorn`) + `.dockerignore`; `docker-compose.yml` estendido com o serviço **`energyhub-api`** e toda a infra numa rede bridge `energyhub-network`, `restart: unless-stopped`, **startup health-gated** (`depends_on: service_healthy`) e config 12-factor por variável de ambiente (URLs por nome de serviço); volumes nomeados para todos os serviços com estado + AOF do Redis; Prometheus passa a scrapear `energyhub-api:8000`. A stack sobe com **um comando** (`docker compose up -d`).
- **Microsserviços + gateway (Fase 15, ⚠️ _breaking_):** monólito decomposto em **5 serviços FastAPI independentes** (`services/auth|client|contract|financial|audit-service/`, portas 8001–8005), cada um com projeto/config/Dockerfile próprios, `mapping.py` enxuto e **banco dedicado**; **Consul** para service discovery (registro + health check + resolução por nome); clientes **`httpx`** (`AuthClient`/`ClientClient`/`ContractClient`) substituindo as chamadas in-process, com **resiliência** (`tenacity`: timeout + retry/backoff + fallback); **Traefik** roteando por prefixo de caminho via catálogo do Consul, com middlewares de borda (auth/logging/rate limit); decomposição documentada em `docs/bounded-contexts.md`.
- **Orquestração com Kubernetes (Fase 16):** árvore `k8s/` (40 manifestos) declarando toda a plataforma — `Namespace` `energyhub`, `Deployment`+`Service`+`HPA` por serviço (réplicas, _requests/limits_, _probes_ `/health`), `ConfigMap`s/`Secret`, `LoadBalancer` (Traefik) + `Ingress` (NGINX) na borda, e backends stateful in-cluster (Postgres/Redis/RabbitMQ/Kafka/Zookeeper). Autoscaling por CPU/memória (2–5 réplicas) via **Metrics Server**. Validado em **minikube** (login→cliente→contrato pelo gateway, HPA escalando 2↔5). Guia em `k8s/README.md`; detalhes em `docs/ARCHITECTURE.md` (§21).
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

## [0.16.0] — 2026-07-13 · ✅ Lançado · _Fase 16 · Kubernetes_

Toda a topologia declarada como manifestos Kubernetes: serviços distribuídos,
auto-recuperáveis, com autoscaling e um único ponto de entrada externo. Validado num
cluster **minikube** local (Kubernetes v1.35). Guia em [`k8s/README.md`](../k8s/README.md).

### Adicionado
- Árvore de manifestos `k8s/` (40 documentos YAML) com `Namespace` `energyhub` e um conjunto por serviço (auth, client, contract, financial, audit) + componentes de plataforma (Consul, Traefik) + backends stateful.
- Um `Deployment` por serviço com `replicas: 2`, _requests/limits_ e _probes_ de _liveness/readiness_ em `/health`; DNS do cluster (`consul-service`, `postgres-service`, …) substitui os hostnames do Compose.
- `ConfigMaps` (configuração não sensível) e um `Secret` (senhas + `*_DATABASE_URL`/`RABBITMQ_URL` que embutem a senha + `SECRET_KEY`), injetados via `envFrom`/`valueFrom` e volume de config.
- `Service` por workload — `ClusterIP` para DNS interno e `LoadBalancer` (Traefik) para a borda; `Ingress` (classe `nginx`) roteando `energyhub.local` até o _gateway_.
- `HorizontalPodAutoscaler` (autoscaling/v2) por serviço — CPU ~70% / memória ~80%, réplicas 2–5 — via **Metrics Server**.
- **Backends stateful in-cluster** (Postgres com _initdb_ dos 5 bancos, Redis, RabbitMQ, Kafka, Zookeeper) para um cluster de dev autocontido — em produção troca-se para managed stores externos ajustando só as URLs no `Secret`.

### Corrigido
- **`enableServiceLinks: false`** nos 5 serviços: as env vars estilo docker-links que o k8s injeta por Service (ex.: `AUTH_SERVICE_PORT=tcp://…`) colidiam com os campos `*_service_port` do `Settings` (pydantic) e quebravam o startup.
- **Kafka** sob k8s: `KAFKA_HEAP_OPTS=-Xmx512m` (evita `OOMKilled`), `strategy: Recreate` (evita disputa de `broker.id` no Zookeeper no rollout) e `publishNotReadyAddresses: true` no Service (o broker se alcança antes do _readiness_).

### Validado
- Todos os pods `Running`/ready; endpoints ligados a pods prontos; comunicação inter-serviço por DNS do cluster; login → criar cliente → criar contrato **pelo gateway** (`200/201/201`); HPA escalando `2 → 5` sob carga e recolhendo para `2`.

### Notas
- **Herdado da Fase 15 (fora do escopo da orquestração):** `register_with_consul` usa `service_id = {name}-{port}` (não único por réplica) — sob `replicas > 1` + rotatividade, o desregistro de uma réplica remove o serviço do Consul; correção adequada (ID por pod) é mudança de imagem. A trilha de auditoria não é auto-populada (nenhum produtor publica na fila `audit`).
- ⚠️ Credenciais placeholder (admin/`ChangeMe123!`, senhas, `SECRET_KEY`, `Secret` só em base64) — rotacionar e migrar para _secret manager_ real antes de qualquer uso não-local.

---

## [0.15.0] — 2026-07-12 · ✅ Lançado · _Fase 15 · Microsserviços_

Decomposição do monólito modular em serviços FastAPI independentemente implantáveis.

### Adicionado
- Documentação dos _bounded contexts_ e do grafo de dependências (`docs/bounded-contexts.md`) — inventário módulo→contexto→serviço, DAG e ordem de extração.
- Extração de **Auth, Clients, Contracts, Financial e Audit** em projetos `services/<nome>-service/` independentes (pyproject, `config.py`, `main.py`, banco dedicado, Dockerfile e `/health` próprios), com `mapping.py` enxuto por serviço.
- _Service discovery_ via **Consul** (`register_with_consul` — auto-registro no startup com _health check_ HTTP e resolução por nome lógico; desregistro no shutdown).
- Comunicação síncrona entre serviços via clientes **httpx** (`AuthClient`, `ClientClient`, `ContractClient`) que substituem as chamadas in-process (notadamente o `get_current_user` dos serviços downstream, que valida o JWT e resolve o usuário no `auth-service`).
- Políticas de resiliência (base `ServiceClient`) com **tenacity**: _timeout_ explícito, _retries_ com _backoff_ exponencial (transientes), _fallback_ `None` e `close` dos pools no shutdown.
- API Gateway **Traefik** roteando por prefixo de caminho via **catálogo do Consul** (rotas vindas das tags de cada serviço), com middlewares de borda: _forwardAuth_ (autenticação), _access log_ e _rate limit_.

### Alterado
- **⚠️ BREAKING:** o ponto de entrada HTTP único é substituído por pontos de entrada por serviço acessados através do _gateway_; chamadas entre módulos passam a ser chamadas de rede e **cada serviço passa a ter o próprio banco de dados** (sem tabelas compartilhadas — referências cross-context viram UUID sem FK).

### Notas
- Validado na stack real (16 containers): os 5 serviços **registram no Consul com health _passing_**; chamadas cross-service (cliente/contrato/fatura) retornam **201** validando o token via `AuthClient`; com o `auth-service` derrubado, uma chamada dependente degrada para **401 contido** (retries + fallback, sem cascata); o **gateway** (`:80`) roteia por prefixo e **bloqueia na borda** requisições sem token (401).
- **Reconciliações:** registro no Consul via **API HTTP** (`httpx`) em vez de `python-consul`; roteamento via **Consul-catalog** (o provider Docker do Traefik não alcança o daemon do Docker Desktop no Windows). O monólito `energyhub-api` permanece no compose (estratégia _strangler_, servindo os contextos ainda não extraídos). Credenciais/`SECRET_KEY` são placeholders a rotacionar antes de produção.

---

## [0.14.0] — 2026-07-12 · ✅ Lançado · _Fase 14 · Containerização_

Aplicação empacotada em imagem Docker _slim_ e _non-root_, com a stack completa
orquestrada por Docker Compose (boot com um único comando).

### Adicionado
- `Dockerfile` _multi-stage_: estágio de _build_ resolve só as deps de produção (`poetry install --only main --no-root`) num venv em `/app/.venv`; estágio de runtime `python:3.12-slim` copia apenas o venv + o código, roda como **`appuser`** (não-root), `EXPOSE 8000` e `CMD uvicorn energyhub.main:app`. `.dockerignore` enxuga o contexto de build.
- Serviço **`energyhub-api`** (construído pelo `Dockerfile`) no `docker-compose.yml`, ao lado de PostgreSQL, Redis, RabbitMQ, Elasticsearch, Kafka + Zookeeper, Prometheus, Grafana e Alertmanager — todos numa rede _bridge_ `energyhub-network` com `restart: unless-stopped`.
- Configuração 12-factor via variáveis de ambiente (`DATABASE_URL`, `REDIS_URL`/`REDIS_HOST`, `RABBITMQ_URL`, `ELASTICSEARCH_URL`, `KAFKA_BOOTSTRAP_SERVERS`, `SECRET_KEY`, `ENVIRONMENT`); todas as URLs endereçam as dependências por **nome de serviço** (não `localhost`), sem segredo embutido na imagem.
- Inicialização **health-gated**: `depends_on: condition: service_healthy` na API para Postgres/Redis/RabbitMQ/Elasticsearch/Kafka (com `start_period` no ES/Kafka para convergência determinística).
- Volumes nomeados para todos os serviços com estado + **AOF do Redis** (dados sobrevivem à recriação dos containers e a ciclos `down`/`up`).
- `prometheus/prometheus.yml` atualizado para scrapear a API por nome de serviço (`energyhub-api:8000`), agora que ela roda na stack.

### Alterado
- Versões de imagem mantidas nas já validadas nas Fases 10–12 (ES `8.13.4`, Kafka/Zookeeper `7.6.1`, Prometheus `v2.54.1`, Grafana `11.2.0`) em vez das do plano (`8.11.0`/`7.5.0`) — um _downgrade_ do Elasticsearch quebraria o volume de dados existente.

### Notas
- Validado na stack real: imagem builda e roda standalone (`/health` 200, processo como `appuser`); `docker compose up -d` sobe 10 serviços saudáveis; **smoke E2E** (login → usuário → cliente → contrato + cache + busca + mensageria) passou; persistência confirmada num ciclo `down`/`up`; RabbitMQ UI, tópicos Kafka, target `energyhub` **UP** no Prometheus e Grafana `:3000` OK.
- **Segurança:** credenciais e `SECRET_KEY` no compose são **placeholders de desenvolvimento** — rotacionar e externalizar (`.env` / secrets manager) antes de produção. Primeiro boot com banco vazio: `docker compose exec energyhub-api alembic upgrade head`.

---

## [0.13.0] — 2026-07-12 · ✅ Lançado · _Fase 13 · Testes & Cobertura_

Suíte de testes determinística (unitários + componente + integração) com _quality gate_ de **80% de cobertura**.

### Adicionado
- Ferramentas de teste (`pytest`, `pytest-mock`, `pytest-asyncio`, `pytest-cov`, `testcontainers`) no grupo `dev` e `[tool.pytest.ini_options]` (modo asyncio `auto`, `testpaths`, padrões de descoberta, marcador `integration`, `addopts` com o gate embutido e `--import-mode=importlib`).
- Testes **unitários** dos 15 serviços da camada de aplicação com colaboradores `AsyncMock` (caminhos felizes e de exceção de domínio, convenção `test_should_..._when_...`); mais value objects, validadores, utilitários, `PageRequest`/`PageResponse`, exception handlers, `JwtService`/hashing e métricas.
- Testes de **componente** dos 13 routers via `TestClient` + `dependency_overrides` (override de `get_current_user`), cobrindo roteamento, status HTTP, serialização e os _guards_ RBAC sem infraestrutura.
- Testes de **integração**: repositórios contra `PostgresContainer` (Testcontainers, com _fallback_ para `EH_TEST_DATABASE_URL`) e API via `TestClient` com login/JWT reais; marcados `integration` e pulados sem Docker.
- Fixtures e _test doubles_ compartilhados em `conftest.py` (doubles `AsyncMock`, cache em memória por teste, harness de router, fixtures de sessão/`TestClient` skip-guarded).
- `docker-compose.test.yml` (PostgreSQL, Redis e RabbitMQ em portas não padrão 5433/6380/5673).
- _Quality gate_ de cobertura (`[tool.coverage.run]`/`[tool.coverage.report]` com `fail_under=80` + `--cov-fail-under=80` no `addopts`) com relatórios HTML e de terminal.

### Corrigido
- Removidos do versionamento 2 `__pycache__/*.pyc` rastreados por engano em `src/energyhub/`.

### Notas
- **Cobertura 87% in-container** (279 testes) / **85% no host** (273 testes, integração pulada). No Windows, o Postgres não é acessível host→container, então a camada de integração roda dentro de um container na rede do compose; unitários/componente rodam no host. A estabilização não revelou defeito de aplicação — apenas ajustes de _harness_ (isolamento de cache em memória; `raise_server_exceptions=False` no `TestClient`).

---

## [0.12.0] — 2026-07-12 · ✅ Lançado · _Fase 12 · Observabilidade_

Visibilidade em tempo real com métricas, dashboards e alertas — o complemento "o que está
acontecendo agora" aos logs. Mudança aditiva e transversal, sem alterar contratos de API existentes.

### Adicionado
- Instrumentação Prometheus via `prometheus-fastapi-instrumentator`: endpoint `/metrics` (excluído da própria instrumentação) com métricas HTTP `fastapi_*` (contagem, latência, in-progress) e `application_info{name,environment,version}` (das settings). Deps `prometheus-client`, `prometheus-fastapi-instrumentator`, `psutil`.
- `MetricsConfig` (`shared/infrastructure/metrics/`) — fábrica única dos coletores customizados (registro exatamente uma vez): `client_created_total`, `contract_created_total{status}`, `invoice_paid_total`, `clients_active` (gauge) e `operation_duration_seconds{endpoint,method}` (histograma).
- `BusinessMetrics` (fachada singleton) + `record_safely` (registro **livre de falhas** — nunca quebra a operação de negócio); séries rotuladas **inicializadas em zero** no lifespan. Serviços instrumentados: `ClientService.create` (duração + `client_created`), `ContractService.create` (por status), `InvoiceService.update` (`invoice_paid` ao transitar para PAID).
- `SystemMetricsCollector` (psutil) — `memory_usage_bytes`/`memory_available_bytes`/`cpu_usage_percent`/`disk_usage_percent`, **refrescados no scrape** (o `collect()` atualiza antes de emitir).
- Serviço **Prometheus** (`prom/prometheus`, `prometheus/prometheus.yml` + volume) que scrapeia o app no host via `host.docker.internal:8000`; **Grafana** (`grafana/grafana`, data source Prometheus provisionado + dashboards de aplicação/negócio/infraestrutura) e **Alertmanager** (`prom/alertmanager`, `alertmanager.yml`) — portas 9090/3000/9093.
- Regras de alerta (`prometheus/alerts.yml`): `HighRequestLatency` (p95 > 1s, warning), `HighErrorRate` (5xx > 5%, critical), `LowMemory` (disponível < 500 MB, warning), roteadas ao Alertmanager.
- Settings `app_version` e `environment` em `energyhub.config.settings`.

### Alterado
- _Override_ de mypy para `psutil` (sem stubs); `prometheus_client` e o instrumentator são tipados.

### Notas
- O `/metrics` fica **aberto** na rede interna (sem auth) e as credenciais do Grafana (`admin`/`admin`) + o receiver do Alertmanager são **placeholders** — trocar antes de qualquer uso não-local.
- O app roda no **host** e o Prometheus o scrapeia via `host.docker.internal` (`extra_hosts: host-gateway` cobre Linux). Prometheus/Grafana/Alertmanager **conectam do host** (como Redis/RabbitMQ/Kafka/ES; só o Postgres falha).

---

## [0.11.0] — 2026-07-12 · ✅ Lançado · _Fase 11 · Busca (Elasticsearch)_

Subsistema de busca _full-text_ com relevância, tolerância a erros e filtros compostos. O
Elasticsearch é um **índice de leitura denormalizado**; o PostgreSQL segue a fonte de verdade e o
índice é reconstruível a partir dele.

### Adicionado
- Serviço `elasticsearch:8.13.4` (single-node, `xpack.security.enabled=false`, heap 512m via `ES_JAVA_OPTS`, _healthcheck_ `_cluster/health`, volume `elasticsearch_data`) no `docker-compose.yml`; dependências `elasticsearch (^8.0)` e `elasticsearch-dsl (^8.0)`.
- Settings `elasticsearch_url` / `elasticsearch_timeout` em `energyhub.config.settings`.
- `ElasticsearchConfig` (`shared/infrastructure/search/`): `get_client()` (cliente síncrono singleton) e `create_indices(documents)` **idempotente** (cria só os índices ausentes; recebe as classes de `Document` do chamador, preservando a regra de dependência).
- Analisador **português** customizado (`portuguese_analyzer`) e documentos `ClientDocument` (índice `clients`) / `ContractDocument` (índice `contracts`) — `Keyword` para filtro exato, `Text` analisado para os nomes, `Date`/`Boolean`/`Double` — com `from_entity` (enums → string, `Decimal` → `float`, id → `meta.id`).
- Repositórios de busca `ClientSearchRepository` / `ContractSearchRepository` (`save`/`delete` + _finders_ estruturados `term`/`match`/`bool`), mantendo o índice sincronizado com o PostgreSQL.
- `ClientSearchService`: `search` (`multi_match` com boosting `corporate_name^2`/`trade_name^1.5`/`cnpj` + `fuzziness='AUTO'`, paginado via `PageRequest`→`PageResponse` com `hits.total.value`), `filter_by_location` e `advanced_search` (query `bool` composta + `min_score`); `ClientMapper.document_to_response_dto`.
- DTOs `SearchFilter` / `FilterCondition` em `shared/application/dto/` (`eq` → term, `gt`/`lt`/`gte`/`lte` → range).
- Router `ClientSearchRouter` sob `/api/v1/search/clients` (GET `/` full-text, GET `/location`, POST `/advanced`), protegido por `CLIENT_READ`; endpoints síncronos (o FastAPI os roda em _threadpool_). Índices criados no **lifespan** da app.
- Testes de busca (`tests/test_search.py`, 6 casos) com **orçamento de latência** (< 1s): full-text/fuzziness, location, paginação, term+range e `min_score`.

### Alterado
- _Override_ de mypy para `elasticsearch_dsl.*` (sem `py.typed`); o cliente `elasticsearch` é tipado.

### Notas
- Índice **secundário**: sem replicação real-time garantida nesta fase (a API de indexação `save`/`delete` existe; a sincronização por eventos sobre a mensageria da Fase 10 fica para depois). Segurança do cluster desabilitada — **apenas dev/local**.
- No Windows/Docker Desktop, o Elasticsearch **conecta do host** (como Redis/RabbitMQ/Kafka; só o Postgres falha); a suíte de busca roda direto do host.

---

## [0.10.0] — 2026-07-12 · ✅ Lançado · _Fase 10 · Mensageria (RabbitMQ & Kafka)_

Comunicação orientada a eventos entre módulos, **fora do caminho da requisição** — RabbitMQ para
workflows por entidade, Kafka para streams de alto volume. A mensageria é um efeito colateral
pós-commit: os serviços permanecem corretos sem os brokers.

### Adicionado
- Broker **RabbitMQ** (`rabbitmq:3-management-alpine`, portas 5672/15672, _healthcheck_ `rabbitmq-diagnostics ping`, volume `rabbitmq_data`) + **Kafka** e **Zookeeper** (`confluentinc/cp-*:7.6.1`, dois _listeners_ — `localhost:9092` p/ host e `kafka:29092` p/ a rede — e `auto-create` desligado) no `docker-compose.yml`; dependências `aio-pika (^9.4)` e `aiokafka (^0.11)`.
- Settings de mensageria (`rabbitmq_url`, `kafka_bootstrap_servers`, `kafka_group_id`) em `energyhub.config.settings`.
- `RabbitMQConfig` (`shared/infrastructure/messaging/`): constantes de **11 filas** por evento (user/client/contract/invoice + notificação + auditoria), `get_url()` (fonte única) e `setup_queues()` que declara todas como `durable=True` de forma **idempotente**.
- `EventProducer` base (conexão robusta preguiçosa, publicação **persistente** `DeliveryMode.PERSISTENT` no _default exchange_) e _producers_ por módulo `UserEventProducer` / `ClientEventProducer`.
- Consumidores `NotificationConsumer` (assina user-created/client-created/contract-approved/invoice-issued) e `AuditConsumer` (persiste um `AuditLog` via `AuditLogRepository`), ambos com **`prefetch_count=1`** e ack pós-processamento (`message.process`); contrato tipado `AuditEvent`.
- `KafkaConfig` (tópicos `user-events`/`client-events`/`contract-events`/`financial-events`, partições por throughput — financeiro com 6 — e `create_topics()` idempotente via `AIOKafkaAdminClient`); `KafkaEventProducer` (`send_and_wait` com chave de partição) e `KafkaEventConsumer` (por tópico, no `kafka_group_id`, `stop` no `finally`).
- Integração nos serviços (publicação **após** a escrita persistida, não-bloqueante): `UserService`/`ClientService` → RabbitMQ; `ContractService`/`InvoiceService` → Kafka (evento sob a chave = id). Helper `publish_safely` loga e engole `MessagePublishingException` sem desfazer a escrita.
- `MessagePublishingException` (`shared/domain/exception/`, `error_code="MESSAGE_PUBLISHING_ERROR"`), encadeada do erro original do broker.

### Alterado
- `main.py` — o `lifespan` passa a preparar a topologia (`setup_queues` + `KafkaConfig.create_topics`, _best-effort_: um broker indisponível apenas gera aviso, não derruba o startup) e a encerrar os produtores compartilhados no shutdown.
- _Override_ de mypy para `aiokafka.*` (sem stubs); `aio-pika` é tipado (o canal é `AbstractChannel`).

### Notas
- **Entrega _at-least-once_:** consumidores confirmam só após o processamento; um handler interrompido causa **redelivery** (validado). Filas duráveis + mensagens persistentes **sobrevivem ao restart** do broker (validado).
- **Dual-write aceito nesta fase:** um broker fora do ar durante a publicação surge como `MessagePublishingException` (logada) sem desfazer o estado já commitado — sem _outbox_ transacional (adiado). Consumidores devem tolerar duplicatas.
- No Windows/Docker Desktop, **RabbitMQ e Kafka conectam do host** (diferente do Postgres); só o E2E que grava no banco (create real, persistência de auditoria) roda no container da rede do compose.

---

## [0.9.0] — 2026-07-12 · ✅ Lançado · _Fase 9 · Cache (Redis)_

_Read-cache_ Redis com invalidação explícita na escrita, sobre os serviços das Fases 6–8.

### Adicionado
- Serviço `redis:7-alpine` (`--appendonly yes`, volume `redis_data`, _healthcheck_ `redis-cli ping`) no `docker-compose.yml`; dependências `redis (^4.6)` e `fastapi-cache2[redis]` (+ `jinja2`, exigido pelo `fastapi-cache2`).
- Settings de conexão Redis (`redis_host`/`redis_port`/`redis_db`/`redis_password` + `redis_url` derivada) em `energyhub.config.settings`.
- `CacheConfig` (`shared/infrastructure/cache/`) inicializando `FastAPICache` com `RedisBackend`, prefixo `energyhub` e **`PickleCoder`** (round-trip fiel de DTOs Pydantic), chamado no **lifespan** da app; `get_cache_key` determinístico + _key builders_ que ignoram o `self`.
- `CacheConstants` com namespaces por domínio (`roles`/`permissions`/`clients`/`contracts`/`users`) e TTLs `SHORT`/`DEFAULT`/`LONG`.
- Cache de leitura via `@cache` nos reads de **5 serviços** (Role, Permission, Client, Contract, User); helpers `invalidate_cache`/`invalidate_all_cache` acionados em **create/update/delete**.
- Permissão `CACHE_MANAGE` (migração **`0010`**, concedida ao ADMIN) e router `/api/v1/cache` (`GET /stats`, `POST /clear`) sob a tag `Cache`, protegido por `require_permission("CACHE_MANAGE")`.

### Alterado
- `main.py` passa a usar `lifespan` (inicializa o cache no startup); `requires-python` limitado a `>=3.12,<4.0` (resolução do `fastapi-cache2`); _overrides_ de mypy para `redis.*` (sem stubs) e para o `[return-value]` da camada de routers (o `@cache` tipa o retorno como `T | Response`).

### Notas
- O cache é um **acelerador best-effort**: os serviços permanecem corretos sem ele. Nesta fase os erros de cache **propagam** (não há _fail-open_) — o Redis do compose é a dependência de runtime dos caminhos cacheados.
- No Windows/Docker Desktop, o Redis **conecta do host** (diferente do Postgres); o E2E do cache roda no container da rede do compose.

---

## [0.8.0] — 2026-07-12 · ✅ Lançado · _Fase 8 · Documentação da API_

API auto-descritiva com contrato OpenAPI curado e erros padronizados (sobre a API/segurança das Fases 6–7).

### Adicionado
- OpenAPI customizado (`custom_openapi()`, cacheado) com título/descrição/versão, metadados de contato/licença e _security scheme_ global `bearerAuth` (HTTP/bearer/JWT); `/docs`, `/redoc` e `/openapi.json` expostos. Rotas públicas (`login`, `/`, `/health`) têm a segurança global neutralizada.
- Documentação por endpoint nos **11 routers**: `summary`, `description` e `responses` por status (compostos de blocos reutilizáveis em `shared/presentation/response/openapi_responses.py`), agrupados em **12 tags** com descrições.
- **30 DTOs** enriquecidos com descrições, exemplos sintéticos e _constraints_ leves (`min_length`/`max_length`/`gt`) que espelham a validação de domínio.
- Esquemas de erro padronizados: `ErrorResponse` (com `error_code`) e `ValidationErrorResponse`/`FieldError`, ambos documentados no OpenAPI.
- Atributo `error_code` (`ClassVar`) nas **23 exceções** de domínio + catálogo `docs/API_ERRORS.md` (status HTTP e códigos por módulo).
- Guia `docs/API_EXAMPLES.md` com exemplos `curl` dos fluxos principais (login → CRUD de clientes) com o cabeçalho `Authorization: Bearer`.

### Alterado
- `ErrorResponse` migrado de _dataclass_ para **Pydantic** (documentado no OpenAPI) e handlers alinhados a emitir os modelos padronizados: `RequestValidationError` → **400** `ValidationErrorResponse` (um item por campo), domínio → 404/409/422 `ErrorResponse`, credenciais inválidas → 401, não-tratado → **500**.
- O esquema de segurança do `HTTPBearer` foi nomeado **`bearerAuth`** (com `bearerFormat=JWT`) para unificar com o documento OpenAPI.
- Versão da aplicação/OpenAPI → **`0.8.0`** (SemVer do projeto; o plano sugeria `1.0.0`, ajustado para consistência — `1.0.0` fica reservado à Fase 17).

### Notas
- Sem `EmailStr` (o pacote `email-validator` não está instalado): campos de e-mail seguem `str` com o `@field_validator` existente.
- CNPJ inválido é rejeitado na camada de _schema_ (Pydantic `@field_validator`) → **400** `ValidationErrorResponse`, não 422.

---

## [0.7.0] — 2026-07-12 · ✅ Lançado · _Fase 7 · Autenticação & RBAC_

Identidade verificada por JWT e acesso controlado por papéis/permissões, sobre a API da Fase 6.

### Adicionado
- Módulo compartilhado de hashing BCrypt (`get_password_hash`, `verify_password`) em `shared/infrastructure/security/password_hasher.py`.
- `JwtService` (python-jose, HS256) que cria, decodifica, valida e extrai o _subject_ dos tokens, lendo `secret_key`/`algorithm`/`access_token_expire_minutes` das _settings_.
- Fluxo de login: `LoginRequestDTO`/`LoginResponseDTO`, `AuthenticationService` (rejeita usuário inexistente, senha errada e conta inativa com o **mesmo** erro) e `AuthRouter` público (`POST /api/v1/auth/login`); handler dedicado que traduz credenciais inválidas em **401** (`WWW-Authenticate: Bearer`).
- Dependência `get_current_user` (`HTTPBearer(auto_error=False)`) + `UserDetails` (papéis e permissões **achatadas**); token ausente/inválido ou _subject_ sem usuário → **401**.
- `require_permission` / `require_role` (em `shared`, encadeados após `get_current_user`) → **403** em grant insuficiente.
- Leitura de papéis/permissões: `RoleService.find_by_name` e `PermissionService.find_by_role_name`.
- **Catálogo de permissões** (`shared/constant/permissions.py`, 38 nomes `<RECURSO>_<AÇÃO>`) e proteção de **10 routers** — `get_current_user` no nível do grupo + **54 guards** `require_permission` por endpoint; login/`/`/`/health` públicos.
- **Migração `0009`**: semeia o catálogo completo de **34 novas permissões** (além das 4 `USER_*` da `0008`) e concede **todas** ao papel `ADMIN` via `INSERT…SELECT` idempotente (à prova de futuro).

### Alterado
- `BaseRouter` ganhou o parâmetro `dependencies` (repassado ao `APIRouter`) para proteção no nível do grupo.
- `password_hasher` passou a expor `get_password_hash` (o `hash_password` da Fase 6 vira _alias_): o plano previa um `passlib` `CryptContext`, mas o `passlib` 1.7.4 é **incompatível** com o `bcrypt 5.x` — mantido o **bcrypt direto** (desvio documentado no módulo).
- `main.py` registra a rota pública de auth, o handler 401, protege os routers de recurso e sobe para a versão **`0.7.0`**; _override_ de mypy para `jose.*` (lib sem stubs).

### Segurança
- JWT _stateless_ (HS256) para escalabilidade horizontal sem sessão compartilhada; token só de acesso (sem _refresh_/revogação nesta fase).
- Senha nunca exposta nos DTOs de resposta; login não revela qual condição falhou.
- ⚠️ `SECRET_KEY` padrão e a credencial semeada `admin` / `ChangeMe123!` (papel `ADMIN`, com **todas** as permissões) **devem ser rotacionadas antes de produção**.

---

## [0.6.0] — 2026-07-12 · ✅ Lançado · _Fase 6 · REST API_

Entidades persistidas expostas como uma API REST documentada (Clean Architecture: DTO → mapper → service → use case → router).

### Adicionado
- DTOs de request/response Pydantic por módulo (auth, clients, contracts, negotiations, financial, audit, notifications, reports) com _constraints_ e metadados OpenAPI; os DTOs de resposta estendem `BaseDTO` e representam relações aninhadas como DTOs próprios.
- Validadores reutilizáveis em `shared/application/validation/` (`validate_cnpj`, `validate_email`, `validate_non_empty`) aplicados via `@field_validator`, e _mappers_ entidade ↔ DTO por módulo.
- Hierarquia de exceções de domínio por módulo (não-encontrado / já-existe) sobre as bases compartilhadas, com um **handler central** (`shared/presentation`) traduzindo `DomainException` em HTTP **404/409/422**.
- Serviços de aplicação (regras de negócio, unicidade, hashing de senha **bcrypt**, resolução de `role_ids`/`permission_ids`) sobre os repositórios da Fase 5, e _use cases_ (`UseCase[Input, Output]`).
- **10 routers / 25 endpoints REST** (`/api/v1/...`, CRUD + listagem paginada + sub-recursos: contatos, pagamentos, transações), registrados em `energyhub.main:app`, com metadados OpenAPI (`/docs`, `/redoc`) e título/versão da API.
- Utilitário de hashing de senha (`shared/infrastructure/security/password_hasher.py`) com `bcrypt` e dependência `bcrypt` declarada.

### Alterado
- `BaseDTO` e `PageResponse` migrados de _dataclass_ para **Pydantic** (herança de auditoria com `from_attributes`; `PageResponse` como `response_model` das listagens).
- No mapeamento ORM (Fase 5), as relações de **navegação** (many-to-one e `Client.contacts`) passaram a `viewonly=True` — as escritas ocorrem só pela FK; sem isso o _flush_ zerava a FK. Escritas M2M (papéis/permissões) usam a relação real.
- `get_session()` passou a **commitar na borda** da requisição (e `rollback` em erro), fechando a unidade de trabalho iniciada na Fase 5.

### Segurança
- Senha do usuário é hasheada no serviço (bcrypt) e **nunca** exposta nos DTOs de resposta.
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
