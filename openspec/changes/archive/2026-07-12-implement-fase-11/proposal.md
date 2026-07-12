## Why

The persistence layer (Fase 5) and messaging (Fase 10) let the platform store and react to data, but the only way to look up clients or contracts is by exact business key or `LOWER(...) LIKE` scans over PostgreSQL — inadequate for the free-text, typo-tolerant, multi-field search that operators need on the catalog. This phase adds a dedicated search subsystem backed by Elasticsearch so entities can be indexed and queried with relevance ranking, fuzziness, and composable filters, without loading the transactional database.

## What Changes

- Add an Elasticsearch service to `docker-compose.yml` (single-node, security disabled for local dev, with a healthcheck and a persistent data volume) and add the `elasticsearch` / `elasticsearch-dsl` dependencies to `pyproject.toml`.
- Add Elasticsearch settings (`elasticsearch_url`, `elasticsearch_timeout`) to `energyhub/config.py` and a shared `ElasticsearchConfig` in `shared/infrastructure/search/` providing a client factory (`get_client`) and index bootstrap (`create_indices`).
- Define `elasticsearch-dsl` `Document` mappings per searchable entity (`ClientDocument`, `ContractDocument`) with typed fields, a Portuguese analyzer, and a `from_entity` factory that projects a domain entity into its search document.
- Add per-module search repositories in `infrastructure/search/` that index (`save`), remove (`delete`), and run term/match finder queries against Elasticsearch, keeping the index in sync with the persistence source of truth.
- Add a full-text search service (`ClientSearchService`) using `multi_match` with field boosting and `fuzziness='AUTO'`, returning paginated `PageResponse` results via a document→DTO mapper method.
- Add advanced filtering: `SearchFilter` / `FilterCondition` DTOs in `shared/application/dto/` and composite `bool` query construction supporting `eq`/`gt`/`lt`/`gte`/`lte` operators and `min_score`.
- Add search routers in `presentation/router/` exposing full-text search, location filtering, and advanced search over HTTP with pagination query parameters.
- Add performance tests asserting search latency budgets and documenting index-tuning levers (keyword fields, analyzers, sharding).

## Capabilities

### New Capabilities

- `elasticsearch-configuration`: Dockerized Elasticsearch service, application settings, and a shared client factory / index bootstrap (`ElasticsearchConfig`).
- `search-document-mapping`: `elasticsearch-dsl` `Document` definitions per searchable entity — typed fields, analyzers, index metadata, and `from_entity` projection from domain entities.
- `entity-indexing`: Per-module search repositories that index, delete, and run term/match finder queries, keeping Elasticsearch synchronized with the persisted entities.
- `full-text-search`: A search service performing relevance-ranked, fuzzy, multi-field `multi_match` queries and returning paginated, mapped result DTOs.
- `advanced-search-filters`: `SearchFilter`/`FilterCondition` DTOs and composite `bool` query building supporting comparison operators and a minimum-score threshold.
- `search-api-endpoints`: HTTP routers exposing full-text search, location filtering, and advanced search with pagination query parameters.
- `search-performance-tests`: Latency-budget tests and index-optimization guidance validating search responsiveness.

### Modified Capabilities

None — this phase introduces the search subsystem; no previously specified requirements change.

## Impact

- **Dependencies**: Adds `elasticsearch` (`^8.0.0`) and `elasticsearch-dsl` (`^8.0.0`) to `pyproject.toml`; adds an `elasticsearch` service and `elasticsearch_data` volume to `docker-compose.yml`.
- **Consumes**: Domain entities and DTOs/mappers from clients and contracts (Fase 3/6), the `PageRequest`/`PageResponse` pagination primitives from Fase 5, and the `BaseRouter` presentation base; reads new `settings.elasticsearch_url` / `settings.elasticsearch_timeout`.
- **Provides**: `energyhub.shared.infrastructure.search.ElasticsearchConfig`, the per-entity search documents and repositories, the search services, the `SearchFilter`/`FilterCondition` DTOs, and the search routers.
- **New artifacts**: `shared/infrastructure/search/` (client config), `shared/application/dto/` (search-filter DTOs), and per-module `infrastructure/search/` (documents + repositories), `application/service/` (search service), and `presentation/router/` (search router).
- **Coordination**: Elasticsearch is a secondary, denormalized read store; PostgreSQL (Fase 4/5) remains the source of truth, and index freshness is bounded by when documents are (re)indexed. Requires the Fase 10 messaging and Docker infrastructure to be running.
