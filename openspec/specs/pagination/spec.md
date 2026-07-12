# pagination Specification

## Purpose
TBD - created by archiving change implement-fase-5. Update Purpose after archive.
## Requirements
### Requirement: Page request primitive

The system SHALL provide a `PageRequest` DTO in `shared/application/dto/` carrying `page`, `size`, optional `sort`, and `direction`, and exposing `get_offset()` and `get_limit()` helpers for translating a page request into SQL offset/limit.

#### Scenario: Offset derived from page and size

- **WHEN** a `PageRequest` with `page=2` and `size=20` computes its offset
- **THEN** `get_offset()` returns `40` and `get_limit()` returns `20`

### Requirement: Page response envelope

The system SHALL provide a generic `PageResponse[T]` DTO carrying `content`, `page_number`, `page_size`, `total_elements`, `total_pages`, `first`, and `last`, with a factory that derives `total_pages`, `first`, and `last` from the inputs.

#### Scenario: Page metadata computed by factory

- **WHEN** `PageResponse.create` is called with `total_elements=45` and `page_size=20`
- **THEN** `total_pages` is `3`, and `first`/`last` correctly reflect whether the current page is the first or last page

#### Scenario: Empty result set

- **WHEN** a page is created with no content and `total_elements=0`
- **THEN** `content` is empty, `total_pages` is `0`, and no error is raised

### Requirement: Paginated repository queries

Repositories SHALL support paginated listing that applies offset/limit and returns both the page content and the total element count needed to build a `PageResponse`.

#### Scenario: Page bounded by limit and offset

- **WHEN** a paginated query is executed for a given `PageRequest`
- **THEN** at most `size` rows are returned starting at the request's offset, and a total count reflecting all matching rows is available

