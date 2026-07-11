## ADDED Requirements

### Requirement: Relevance-ranked full-text search

The system SHALL provide a search service (e.g. `ClientSearchService`) that runs a `multi_match` query across multiple fields with per-field boosting and `fuzziness='AUTO'`, ranking results by relevance.

#### Scenario: Query matches across multiple fields

- **WHEN** the search service is called with a free-text query
- **THEN** a `multi_match` query is executed over the configured fields with boosting (e.g. `corporate_name` weighted above `trade_name` and `cnpj`) and results are ordered by relevance score

#### Scenario: Typo tolerance via fuzziness

- **WHEN** the query contains a minor spelling variation of an indexed term
- **THEN** the `fuzziness='AUTO'` setting still matches the intended documents

### Requirement: Paginated search results

The search service SHALL apply the offset/limit derived from a `PageRequest` and return a `PageResponse` whose `total_elements` reflects the total number of matching hits.

#### Scenario: Page bounded by the request

- **WHEN** a search is executed for a `PageRequest` with a given page and size
- **THEN** at most `size` results starting at the request's offset are returned, and `total_elements` equals the total hit count reported by Elasticsearch

### Requirement: Document-to-DTO mapping

The search service SHALL map returned search documents into response DTOs via a mapper method (e.g. `document_to_response_dto`) so the search API returns the same DTO shape as the rest of the module.

#### Scenario: Documents mapped to response DTOs

- **WHEN** search results are assembled into a `PageResponse`
- **THEN** each returned document is converted to its response DTO before being placed in the page content
