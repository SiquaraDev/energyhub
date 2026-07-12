# query-filtering Specification

## Purpose
TBD - created by archiving change implement-fase-5. Update Purpose after archive.
## Requirements
### Requirement: Reusable SQLAlchemy filter builders

The system SHALL provide filter/specification classes (at least `ClientFilter` and `ContractFilter`) whose methods each return a composable SQLAlchemy condition, so queries can be assembled from named, reusable predicates.

#### Scenario: Filter methods return composable conditions

- **WHEN** a filter builder method such as `ClientFilter.has_cnpj(cnpj)` or `ClientFilter.is_active()` is called
- **THEN** it returns a SQLAlchemy expression that can be combined with others via `and_`/`or_` in a `select` statement

#### Scenario: Contract activity window filter

- **WHEN** `ContractFilter.is_active_between(start_date, end_date)` is used in a query
- **THEN** only contracts whose date range overlaps the given window are matched

### Requirement: Pydantic filter DTOs for advanced queries

The system SHALL provide Pydantic filter DTOs (at least `ClientFilterDTO` and `ContractFilterDTO`) exposing optional criteria fields, so callers supply only the fields they want to filter on.

#### Scenario: Optional fields default to unset

- **WHEN** a `ClientFilterDTO` is created with only `cnpj` provided
- **THEN** the remaining fields default to `None` and are ignored when building the query

#### Scenario: Filter DTO drives conditional predicates

- **WHEN** a repository builds a query from a filter DTO
- **THEN** only the DTO fields that are set contribute predicates, and unset fields add no constraint

