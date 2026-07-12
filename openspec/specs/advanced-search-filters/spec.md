# advanced-search-filters Specification

## Purpose
TBD - created by archiving change implement-fase-11. Update Purpose after archive.
## Requirements
### Requirement: Search filter DTOs

The system SHALL provide `SearchFilter` and `FilterCondition` Pydantic DTOs in `shared/application/dto/` that carry an optional query, target fields, fuzziness, a minimum score, and a list of field/operator/value filter conditions.

#### Scenario: Filter DTO carries optional criteria

- **WHEN** a `SearchFilter` is constructed with only some fields populated
- **THEN** the unset fields default to absent and do not contribute any query clauses

#### Scenario: Filter condition carries an operator

- **WHEN** a `FilterCondition` is constructed
- **THEN** it holds a `field`, an `operator` from the supported set (`eq`, `gt`, `lt`, `gte`, `lte`), and a `value`

### Requirement: Composite boolean query construction

The system SHALL translate a `SearchFilter` into a composite `bool` query, combining an optional `multi_match` clause with per-condition `term` (for `eq`) and `range` (for `gt`/`lt`/`gte`/`lte`) filter clauses.

#### Scenario: Equality condition becomes a term filter

- **WHEN** a filter condition with operator `eq` is applied
- **THEN** a `term` clause on the condition's field and value is added to the `bool` query's filter context

#### Scenario: Comparison condition becomes a range filter

- **WHEN** a filter condition with operator `gte` (or `gt`/`lt`/`lte`) is applied
- **THEN** a `range` clause with the corresponding bound is added to the `bool` query's filter context

#### Scenario: Filters compose with the text query

- **WHEN** a `SearchFilter` supplies both a query and one or more conditions
- **THEN** the resulting `bool` query requires the text match and all filter conditions together

### Requirement: Minimum-score threshold

Advanced search SHALL support an optional minimum-score threshold that excludes results scoring below the configured value.

#### Scenario: Low-relevance results excluded

- **WHEN** a `SearchFilter` sets `min_score`
- **THEN** the executed search applies that minimum score and documents scoring below it are omitted from the results

