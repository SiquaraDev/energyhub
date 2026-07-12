# search-document-mapping Specification

## Purpose
TBD - created by archiving change implement-fase-11. Update Purpose after archive.
## Requirements
### Requirement: Search document definitions per entity

The system SHALL define an `elasticsearch-dsl` `Document` per searchable entity — `ClientDocument` and `ContractDocument` — declaring typed fields and index metadata, placed under each module's `infrastructure/search/` package.

#### Scenario: Client document declares typed fields and index name

- **WHEN** the `ClientDocument` mapping is inspected
- **THEN** it declares `Keyword` fields for exact-match attributes (e.g. `cnpj`, `email`, `city`, `state`), `Text` fields for free-text attributes (e.g. `corporate_name`, `trade_name`), and binds to the `clients` index

#### Scenario: Contract document declares typed fields and index name

- **WHEN** the `ContractDocument` mapping is inspected
- **THEN** it declares `Keyword` fields for identifiers and status/type, `Date` fields for start/end dates, a `Double` field for `total_value`, and binds to the `contracts` index

### Requirement: Language-aware text analysis

Free-text fields SHALL be analyzed with a Portuguese analyzer so that search matching accounts for language-specific stopwords and normalization.

#### Scenario: Text fields use the Portuguese analyzer

- **WHEN** a `Text` field such as `corporate_name` is mapped
- **THEN** it is configured to use the Portuguese analyzer defined in the index settings

### Requirement: Projection from domain entity to document

Each search document SHALL provide a `from_entity` factory that projects a domain entity into its search document, converting non-primitive attributes (e.g. enums, `Decimal`, ids) into index-safe types.

#### Scenario: Entity is projected into a search document

- **WHEN** `ClientDocument.from_entity(client)` is called with a domain client
- **THEN** it returns a document whose fields are populated from the entity, with the id stringified and non-primitive values converted to indexable types

