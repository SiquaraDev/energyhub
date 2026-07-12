## Context

The platform persists clients, contracts, and related entities in PostgreSQL (Fase 4/5) and reacts to domain events over messaging (Fase 10). Lookups today are limited to exact business keys and `LOWER(...) LIKE` scans, which do not support free-text relevance ranking, typo tolerance, or multi-field weighting. This phase introduces a dedicated search subsystem backed by Elasticsearch, fitted into the existing Clean Architecture layout: search documents and repositories live in each module's `infrastructure/search/`, search services in `application/service/`, transport DTOs in `application`/`shared/application/dto/`, and routers in `presentation/router/`.

The stack is fixed by the plan: Elasticsearch 8.x running as a single-node Docker Compose service (security disabled for local development), accessed via `elasticsearch` and `elasticsearch-dsl` 8.x. Configuration is single-sourced through `energyhub.config.settings` (`elasticsearch_url`, `elasticsearch_timeout`), consistent with how the database and messaging are configured. Prerequisites are Fase 10 (messaging) and a working Docker environment.

Elasticsearch is a secondary, denormalized read store. PostgreSQL remains the source of truth; the search index is a projection that must be populated and kept in sync. This phase establishes the indexing and query surface; the eventual event-driven synchronization pathway (consuming domain events to reindex) builds on the Fase 10 messaging already in place.

## Goals / Non-Goals

**Goals:**
- Run Elasticsearch as a Dockerized service and provide a shared client factory and idempotent index bootstrap (`ElasticsearchConfig`).
- Define per-entity `elasticsearch-dsl` documents with typed fields, a Portuguese analyzer, and `from_entity` projection.
- Provide search repositories that index, delete, and run structured finder queries.
- Provide a relevance-ranked, fuzzy, paginated full-text search service returning response DTOs.
- Provide advanced filtering (`SearchFilter`/`FilterCondition`) with composite `bool` queries and a minimum-score threshold.
- Expose search over HTTP via routers, and validate responsiveness with performance tests.

**Non-Goals:**
- No replacement of PostgreSQL as the system of record; Elasticsearch is a read-optimized projection only.
- No fully automated, guaranteed real-time reindex pipeline in this phase — the indexing API is provided; event-driven sync wiring is deferred.
- No cross-cluster replication, multi-node topology, or production security hardening (single-node, security disabled locally).
- No new domain entities or persistence schema changes; searchable data is projected from existing entities.
- No aggregation/analytics dashboards or autocomplete/suggesters beyond the described full-text and filter queries.

## Decisions

**Elasticsearch as a secondary read store, PostgreSQL remains source of truth:**
- **Decision:** Index a denormalized projection of clients and contracts into Elasticsearch and serve search from it; never treat the index as authoritative.
- **Rationale:** Keeps heavy free-text queries off the transactional database and lets the index be rebuilt from PostgreSQL at any time, so index loss is recoverable rather than catastrophic.
- **Alternative considered:** PostgreSQL full-text search (`tsvector`/`GIN`) — rejected because it does not match the plan's Elasticsearch requirement and offers weaker relevance tuning, boosting, and fuzziness ergonomics for this catalog-search use case.

**`elasticsearch-dsl` `Document` classes with `from_entity`, separate from ORM entities:**
- **Decision:** Model each searchable entity as its own `Document` (`ClientDocument`, `ContractDocument`) with a `from_entity` factory, rather than reusing the SQLAlchemy ORM entities.
- **Rationale:** The search projection is denormalized and typed for the index (keyword vs. text, enums flattened to strings, `Decimal`→`Double`, ids stringified); coupling it to the ORM model would leak persistence concerns and force awkward dual mappings.
- **Alternative considered:** Annotate ORM entities to double as search documents — rejected; it conflates two stores with different field semantics and lifecycles.

**Keyword vs. Text field split with a Portuguese analyzer:**
- **Decision:** Map exact-match attributes (cnpj, email, city, state, status, ids) as `Keyword` and human-language attributes (corporate/trade name, client name) as `Text` analyzed with a Portuguese analyzer.
- **Rationale:** Keyword fields give precise term/range filtering and aggregation; analyzed text fields give language-aware, stopword-stripped relevance matching — the two query modes the API needs.
- **Alternative considered:** Analyze all fields uniformly — rejected; analyzing identifiers breaks exact filtering, and leaving names unanalyzed breaks relevance search.

**Two-layer filtering — repository finders vs. `SearchFilter` DTO + composite `bool` builder:**
- **Decision:** Provide fixed structured finders on the repository for common lookups, and a generic `SearchFilter`/`FilterCondition` translated into a composite `bool` query for advanced, user-driven filtering with `eq`/`gt`/`lt`/`gte`/`lte` operators.
- **Rationale:** Common paths stay simple and named; advanced needs are covered by one composable builder instead of an ever-growing set of bespoke methods. Mirrors the filter/DTO split established for persistence in Fase 5.
- **Alternative considered:** Only bespoke finder methods — rejected as combinatorially unscalable; only a raw query passthrough — rejected as it leaks Elasticsearch query syntax to callers.

**Offset/limit pagination reusing Fase 5 `PageRequest`/`PageResponse`:**
- **Decision:** Drive search paging from the existing `PageRequest` (offset/limit) and assemble a `PageResponse` using the hit total from Elasticsearch (`response.hits.total.value`).
- **Rationale:** Consistency with the persistence-layer pagination contract so the search API returns the same envelope as the rest of the platform.
- **Alternative considered:** `search_after`/cursor pagination — rejected as premature; offset/limit is sufficient for admin-style search over the expected data volumes.

**`multi_match` with field boosting and `fuzziness='AUTO'`:**
- **Decision:** Full-text search uses a single `multi_match` across weighted fields (e.g. `corporate_name^2`, `trade_name^1.5`, `cnpj`) with `fuzziness='AUTO'`.
- **Rationale:** One query expresses cross-field relevance and typo tolerance with minimal code, matching the plan's examples.
- **Alternative considered:** Separate per-field queries combined manually — rejected as more code with no added control for this use case.

## Risks / Trade-offs

- **Index/source drift** (Elasticsearch documents lag or diverge from PostgreSQL) → This phase provides `save`/`delete` indexing and idempotent bootstrap; treat the index as rebuildable from the source of truth and defer guaranteed real-time sync to an event-driven consumer built on Fase 10 messaging.
- **Security disabled on the local cluster** → Acceptable for local/dev only; production hardening (auth, TLS, network isolation) is out of scope here and must be addressed before any non-local deployment.
- **Analyzer/type mismatches degrade results** (identifier analyzed, or name left unanalyzed) → Enforce the keyword/text split in the document mappings and cover it with the structured-finder and full-text tests.
- **Unbounded or deep-offset queries** → Default all search endpoints to pagination; deep offsets are a known Elasticsearch cost and are bounded by validated `size` limits, with cursor paging available later if needed.
- **Resource footprint of Elasticsearch** (JVM heap, disk) → Constrain heap via `ES_JAVA_OPTS` and back data with a dedicated volume; single-node is sufficient for development.
- **Performance regressions under growth** → The performance tests set a latency budget and the change documents tuning levers (keyword fields, analyzer tuning, sharding) so responses can be restored without changing the public search contract.

## Migration Plan

1. Add the `elasticsearch` service and `elasticsearch_data` volume to `docker-compose.yml`, bring it up, and confirm `_cluster/health` is reachable.
2. Add `elasticsearch`/`elasticsearch-dsl` dependencies and the `elasticsearch_url`/`elasticsearch_timeout` settings; add `ElasticsearchConfig` and confirm the client connects.
3. Define the `ClientDocument`/`ContractDocument` mappings with the Portuguese analyzer and `from_entity`; run `create_indices()` and verify the indices exist.
4. Add the search repositories (index/delete + structured finders), then the full-text search service and document→DTO mapper method.
5. Add the `SearchFilter`/`FilterCondition` DTOs and composite `bool` query building; add the search routers exposing full-text, location, and advanced search.
6. Add performance tests and run the suite (`poetry run pytest tests/ -k search`).
7. Rollback: this phase is additive and isolated to the search subsystem; reverting the branch and removing the Elasticsearch service leaves PostgreSQL and existing features untouched.

## Open Questions

- How should the index be kept in sync with PostgreSQL — synchronously in the write path, or asynchronously via a domain-event consumer on the Fase 10 messaging bus? (Current plan: provide the indexing API now; wire event-driven sync in a later phase.)
- Which entities beyond clients and contracts warrant a search index (e.g. negotiations, invoices)? (Deferred; start with the two entities the plan specifies.)
- What is the concrete latency budget and dataset size the performance tests should assert against? (Plan uses a sub-second budget on a representative query; confirm with expected production volumes.)
- Should a single shared search API surface be exposed, or one router per module? (Current plan: one router per module, mounted alongside the module's other routes.)
