## 1. Elasticsearch Infrastructure

- [ ] 1.1 Add the `elasticsearch` service (single-node, `xpack.security.enabled=false`, bounded `ES_JAVA_OPTS`) and an `elasticsearch_data` volume to `docker-compose.yml`
- [ ] 1.2 Add the cluster-health `healthcheck` to the service and start it (`docker-compose up -d elasticsearch`)
- [ ] 1.3 Confirm the cluster responds (`curl http://localhost:9200` and `curl http://localhost:9200/_cluster/health`)
- [ ] 1.4 Add `elasticsearch` and `elasticsearch-dsl` (`^8.0.0`) to `pyproject.toml` and install (`poetry add elasticsearch elasticsearch-dsl`)
- [ ] 1.5 Add `elasticsearch_url` and `elasticsearch_timeout` settings to `energyhub/config.py`

## 2. Client Configuration and Index Bootstrap

- [ ] 2.1 Create `shared/infrastructure/search/elasticsearch_config.py` with `ElasticsearchConfig.get_client()` reading `settings.elasticsearch_url`/`elasticsearch_timeout`
- [ ] 2.2 Implement `ElasticsearchConfig.create_indices()` that initializes each index only when it does not already exist (idempotent)
- [ ] 2.3 Confirm the client connects and `create_indices()` runs without error against the running container

## 3. Search Document Mapping

- [ ] 3.1 Define the Portuguese analyzer in the index settings for text fields
- [ ] 3.2 Create `ClientDocument` in `clients/infrastructure/search/` with `Keyword` fields (cnpj, email, city, state), `Text` fields (corporate_name, trade_name) using the Portuguese analyzer, `Boolean`/`Date` fields, and the `clients` index
- [ ] 3.3 Create `ContractDocument` in `contracts/infrastructure/search/` with keyword identifiers/status/type, `Date` fields, a `Double` `total_value`, and the `contracts` index
- [ ] 3.4 Add `from_entity` factories converting enums to strings, `Decimal` to `float`, and ids to strings

## 4. Search Repositories (Indexing)

- [ ] 4.1 Create `ClientSearchRepository` in `clients/infrastructure/search/` constructed with `ElasticsearchConfig.get_client()`
- [ ] 4.2 Implement `save` (index a document) and `delete` (remove by id)
- [ ] 4.3 Implement structured finders `find_by_corporate_name_containing`, `find_by_city_and_state`, and `find_by_active_true`
- [ ] 4.4 Create the equivalent `ContractSearchRepository` with its structured finders

## 5. Full-Text Search Service

- [ ] 5.1 Create `ClientSearchService` in `clients/application/service/` taking the search repository and mapper
- [ ] 5.2 Implement `search` using a `multi_match` query with field boosting (`corporate_name^2`, `trade_name^1.5`, `cnpj`) and `fuzziness='AUTO'`
- [ ] 5.3 Apply `PageRequest` offset/limit and build a `PageResponse` using `response.hits.total.value` as `total_elements`
- [ ] 5.4 Add `document_to_response_dto` to the client mapper and use it to populate page content
- [ ] 5.5 Implement `filter_by_location` returning a paginated `PageResponse` for city/state

## 6. Advanced Search Filters

- [ ] 6.1 Create `FilterCondition` and `SearchFilter` DTOs in `shared/application/dto/` (query, fields, fuzzy, min_score, conditions)
- [ ] 6.2 Implement `advanced_search` building a composite `bool` query from an optional `multi_match` plus per-condition clauses
- [ ] 6.3 Map `eq` to `term` filters and `gt`/`lt`/`gte`/`lte` to `range` filters in the filter context
- [ ] 6.4 Apply the optional `min_score` threshold and return a paginated `PageResponse`

## 7. Search API Endpoints

- [ ] 7.1 Create `ClientSearchRouter` in `clients/presentation/router/` extending `BaseRouter`
- [ ] 7.2 Register the full-text search route (`GET /`) with `q`, `page`, and `size` query parameters (validated ranges)
- [ ] 7.3 Register the location filter route (`GET /location`) with `city`, `state`, and pagination
- [ ] 7.4 Wire the router to `ClientSearchService` and mount it in the application

## 8. Performance Tests and Optimization

- [ ] 8.1 Populate a representative test index for search assertions
- [ ] 8.2 Add a performance test asserting a representative search completes within the latency budget and returns results
- [ ] 8.3 Run the suite (`poetry run pytest tests/ -k search`)
- [ ] 8.4 Document the index-tuning levers (additional keyword fields, analyzer adjustments, sharding) for latency regressions

## 9. Validation

- [ ] 9.1 Confirm Elasticsearch is configured, healthy, and indices are created
- [ ] 9.2 Verify entities are indexed and returned by full-text search, location filter, and advanced filters
- [ ] 9.3 Verify pagination and `min_score` behave as specified
- [ ] 9.4 Run `openspec validate implement-fase-11` and confirm the change is valid
