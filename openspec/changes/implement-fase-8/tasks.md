## 1. OpenAPI Configuration

- [ ] 1.1 Set `FastAPI(title="EnergyHub API", description=..., version="1.0.0")` and configure `docs_url="/docs"`, `redoc_url="/redoc"`, `openapi_url="/openapi.json"` in `energyhub/main.py`
- [ ] 1.2 Add a `custom_openapi()` builder that returns the cached `app.openapi_schema` when present and otherwise builds it via `get_openapi(...)`
- [ ] 1.3 Inject `info.contact` and `info.license` metadata into the generated schema
- [ ] 1.4 Add the `bearerAuth` HTTP/bearer/JWT `securityScheme` under `components.securitySchemes` and set the global `security` requirement
- [ ] 1.5 Assign `app.openapi = custom_openapi`, start the app, and confirm `/docs`, `/redoc`, and `/openapi.json` all render

## 2. Endpoint Documentation

- [ ] 2.1 Add `summary` and `description` to every route registered via `add_api_route` in the auth router
- [ ] 2.2 Add `summary`, `description`, and per-status `responses` to every route in the clients router (`201`/`400`/`409`, `200`/`404`, list `200`)
- [ ] 2.3 Add the same route metadata to the remaining module routers (contracts, negotiations, financial, and others)
- [ ] 2.4 Document list-endpoint query parameters (`page`, `size`, `sort`, `direction`) with descriptions and bounds via `Query(...)`
- [ ] 2.5 Add `tags` (e.g. `Authentication`, `Clients`) when including each router in `main.py` and confirm grouping in Swagger UI

## 3. Schema Documentation

- [ ] 3.1 Annotate auth DTO fields (`UserRequestDTO`, login DTOs) with `Field(description=..., example=...)` and constraints (`min_length`, `EmailStr`)
- [ ] 3.2 Annotate client DTO fields (`ClientRequestDTO`, `ClientResponseDTO`) with descriptions, constraints, and examples
- [ ] 3.3 Annotate the remaining request/response DTOs across modules with descriptions and examples
- [ ] 3.4 Reload the docs and confirm schemas render descriptions and example payloads in Swagger UI

## 4. Error Response Schemas

- [ ] 4.1 Create `shared/presentation/response/error_response.py` with `ErrorResponse` (`timestamp`, `status`, `error`, `message`, `path`) using documented `Field`s
- [ ] 4.2 Create `shared/presentation/response/validation_error_response.py` with `FieldError` and `ValidationErrorResponse` (`status`, `message`, `errors`)
- [ ] 4.3 Update the validation handler to return a `ValidationErrorResponse` with one `FieldError` per invalid field and status `400`
- [ ] 4.4 Update the `ResourceNotFoundException` handler to return an `ErrorResponse` with status `404` and the request path
- [ ] 4.5 Register the handlers in `energyhub/main.py` and document these models as the `responses` for the relevant error statuses
- [ ] 4.6 Trigger a `404` and a validation error and confirm the response bodies match the documented schemas

## 5. Error Catalog

- [ ] 5.1 Add an `error_code` attribute (with a sensible default) to `ResourceNotFoundException` and the other domain exceptions
- [ ] 5.2 Create `docs/API_ERRORS.md` documenting the generic HTTP status codes (`400`, `401`, `403`, `404`, `409`, `422`, `500`) with descriptions and common causes
- [ ] 5.3 Add module-specific error codes to `docs/API_ERRORS.md` (authentication, clients, contracts) with explanations

## 6. API Usage Examples

- [ ] 6.1 Create `docs/API_EXAMPLES.md` with a `curl` login example and a representative JSON response containing an access token
- [ ] 6.2 Add `curl` examples for creating, listing, and fetching a client, including the `Authorization: Bearer <TOKEN>` header on protected calls

## 7. Validation

- [ ] 7.1 Confirm the OpenAPI document exposes the configured metadata and `bearerAuth` scheme and that Swagger UI, ReDoc, and `/openapi.json` are reachable
- [ ] 7.2 Confirm endpoints show summaries, documented responses, and tags, and that DTO schemas show descriptions and examples
- [ ] 7.3 Confirm error responses conform to `ErrorResponse`/`ValidationErrorResponse` and that `docs/API_ERRORS.md` and `docs/API_EXAMPLES.md` are complete
- [ ] 7.4 Run `openspec validate implement-fase-8` and confirm the change is valid
