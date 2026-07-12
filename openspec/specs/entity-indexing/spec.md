# entity-indexing Specification

## Purpose
TBD - created by archiving change implement-fase-11. Update Purpose after archive.
## Requirements
### Requirement: Per-module search repositories

The system SHALL provide a search repository per searchable module (e.g. `ClientSearchRepository`) under `infrastructure/search/`, each constructed with an Elasticsearch client obtained from `ElasticsearchConfig`.

#### Scenario: Repository is bound to an Elasticsearch client

- **WHEN** a search repository is instantiated
- **THEN** it holds an Elasticsearch client from `ElasticsearchConfig.get_client()` and directs all its operations at that client

### Requirement: Index and remove documents

Search repositories SHALL expose operations to index (`save`) a document and to remove (`delete`) a document by id, so the search index can be kept synchronized with the persisted source of truth.

#### Scenario: Save indexes a document

- **WHEN** `save` is called with a document
- **THEN** the document is persisted to its index and becomes retrievable by subsequent searches

#### Scenario: Delete removes a document by id

- **WHEN** `delete` is called with a document id
- **THEN** the document with that id is removed from the index and no longer appears in search results

### Requirement: Structured finder queries

Search repositories SHALL expose structured finder methods that run `term`/`match`/`bool` queries for common lookups (e.g. `find_by_corporate_name_containing`, `find_by_city_and_state`, `find_by_active_true`) and return the matching documents.

#### Scenario: Term filter returns matching documents

- **WHEN** `find_by_city_and_state` is called with a city and state
- **THEN** only documents whose `city` and `state` keyword fields match both terms are returned

#### Scenario: Boolean flag filter

- **WHEN** `find_by_active_true` is called
- **THEN** only documents whose `active` field is `true` are returned

