# openapi-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-8. Update Purpose after archive.
## Requirements
### Requirement: Customized OpenAPI metadata

The FastAPI application SHALL publish an OpenAPI document whose `info` block carries a title (`EnergyHub API`), a description, and a version, and SHALL enrich it via a `custom_openapi()` builder that injects `contact` and `license` metadata.

#### Scenario: OpenAPI document exposes API metadata

- **WHEN** a client requests the generated OpenAPI schema
- **THEN** the `info` object contains the configured title, description, version, and the injected `contact` and `license` fields

#### Scenario: Custom schema is built once and cached

- **WHEN** the OpenAPI schema is requested more than once
- **THEN** the `custom_openapi()` builder returns the previously generated schema instead of rebuilding it

### Requirement: Documentation UIs exposed

The application MUST expose the interactive documentation endpoints: Swagger UI at `/docs`, ReDoc at `/redoc`, and the raw schema at `/openapi.json`.

#### Scenario: Swagger UI is reachable

- **WHEN** a client navigates to `/docs`
- **THEN** the Swagger UI renders the API operations from the OpenAPI schema

#### Scenario: Raw OpenAPI JSON is reachable

- **WHEN** a client requests `/openapi.json`
- **THEN** the server returns the OpenAPI document as JSON

### Requirement: Global JWT security scheme

The OpenAPI document SHALL declare a `bearerAuth` security scheme of type `http`, scheme `bearer`, bearer format `JWT`, and apply it as a global security requirement so protected operations render an authorize control.

#### Scenario: Bearer security scheme is documented

- **WHEN** the OpenAPI schema is generated
- **THEN** `components.securitySchemes.bearerAuth` describes an HTTP bearer JWT scheme and the document declares a global `security` requirement referencing it

