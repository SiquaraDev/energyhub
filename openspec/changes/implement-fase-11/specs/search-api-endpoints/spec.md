## ADDED Requirements

### Requirement: Search router

The system SHALL provide a search router (e.g. `ClientSearchRouter`) under `presentation/router/` that extends the shared `BaseRouter` and registers the search endpoints for its module.

#### Scenario: Router registers search routes

- **WHEN** the search router is initialized
- **THEN** it registers its HTTP routes on the shared router and is mountable by the application

### Requirement: Full-text search endpoint

The search API SHALL expose a full-text search endpoint accepting a required query parameter and pagination parameters (`page`, `size`) and returning a paginated `PageResponse` of response DTOs.

#### Scenario: Search endpoint returns a page of results

- **WHEN** a `GET` request is made to the search endpoint with a query and pagination parameters
- **THEN** the endpoint delegates to the search service and returns a `PageResponse` containing the matching response DTOs

#### Scenario: Pagination parameters are bounded

- **WHEN** the request supplies `page` and `size` query parameters
- **THEN** `page` is validated as non-negative and `size` is validated within its allowed range before the search runs

### Requirement: Location filter endpoint

The search API SHALL expose a location filter endpoint that filters entities by city and state with pagination.

#### Scenario: Location endpoint filters by city and state

- **WHEN** a `GET` request is made to the location endpoint with `city` and `state`
- **THEN** the endpoint returns a paginated `PageResponse` of entities matching both the city and the state
