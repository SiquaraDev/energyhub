## 1. Request/Response DTOs

- [ ] 1.1 Create `auth/application/dto/` request/response DTOs: `UserRequestDTO`, `UserResponseDTO`, `RoleResponseDTO`, `PermissionResponseDTO` with field constraints and `Field(...)` descriptions
- [ ] 1.2 Create `clients/application/dto/` DTOs: `ClientRequestDTO`, `ClientResponseDTO`, `ContactRequestDTO`, `ContactResponseDTO`
- [ ] 1.3 Create `contracts/application/dto/` DTOs: `ContractRequestDTO`, `ContractResponseDTO`
- [ ] 1.4 Create the remaining module DTOs: `NegotiationRequestDTO`/`Response`, `EnergyTransactionRequestDTO`/`Response`, `InvoiceRequestDTO`/`Response`, `PaymentRequestDTO`/`Response`
- [ ] 1.5 Ensure every response DTO extends the shared `BaseDTO` (exposes `id`, `created_at`, `updated_at`) and nests related response DTOs
- [ ] 1.6 Confirm a sample valid payload validates and an invalid one raises a Pydantic error for each request DTO

## 2. Input Validation

- [ ] 2.1 Create `shared/application/validation/` with `CnpjValidator` and any other reusable validators as standalone functions
- [ ] 2.2 Add a unit check that the validator accepts a valid value and rejects a malformed one
- [ ] 2.3 Apply validators to the relevant request DTOs via `@field_validator` (e.g. `cnpj`, non-empty `username`/`name`)

## 3. Domain Exceptions

- [ ] 3.1 Create `auth/domain/exception/`: `UserNotFoundException`, `UserAlreadyExistsException`, `InvalidCredentialsException`
- [ ] 3.2 Create `clients/domain/exception/`: `ClientNotFoundException`, `ClientAlreadyExistsException`, `InvalidCnpjException`
- [ ] 3.3 Create `contracts/domain/exception/`: `ContractNotFoundException`, `ContractAlreadyExistsException`, `InvalidContractStatusException`
- [ ] 3.4 Ensure each domain exception extends the shared `ResourceNotFoundException` or `ValidationException`

## 4. Entity/DTO Mappers

- [ ] 4.1 Create `auth/application/mapper/UserMapper` with `to_entity`, `to_response_dto`, and nested role/permission mapping
- [ ] 4.2 Create `clients/application/mapper/ClientMapper` with `to_entity`, `to_response_dto`, and contact entity/DTO mapping
- [ ] 4.3 Create mappers for the remaining modules (contracts, negotiations, financial)
- [ ] 4.4 Verify a create-then-read round-trip maps every response field (no silent omissions), including nested relations

## 5. Application Services

- [ ] 5.1 Create `auth/application/service/UserService` (constructor-injected repositories + mapper) with `create`, `find_by_id`, `update`, `delete`
- [ ] 5.2 Enforce username/email uniqueness in `UserService.create`, hash the password with `passlib`, and resolve `role_ids` to roles
- [ ] 5.3 Create `clients/application/service/ClientService` with `create`, `find_by_id`, `find_all`, `update`, `delete` and CNPJ uniqueness
- [ ] 5.4 Back `find_all` with the Fase 5 paginated query (bounded `select` + `count()`) returning a `PageResponse` of DTOs
- [ ] 5.5 Create services for the remaining modules with existence checks and not-found/already-exists exceptions
- [ ] 5.6 Confirm services flush via repositories but leave commit to the request-scoped session

## 6. Use Cases

- [ ] 6.1 Create `auth/application/usecase/CreateUserUseCase` extending `UseCase[UserRequestDTO, UserResponseDTO]` delegating to `UserService`
- [ ] 6.2 Create `clients/application/usecase/CreateClientUseCase` extending the shared `UseCase` contract
- [ ] 6.3 Add the remaining use cases (create/update/delete per aggregate) delegating to their services
- [ ] 6.4 Confirm use cases embed no persistence or mapping logic and propagate domain exceptions unchanged

## 7. REST Routers

- [ ] 7.1 Create `auth/presentation/router/UserRouter` extending `BaseRouter`, registering POST/GET/PUT/DELETE bound to `UserService`
- [ ] 7.2 Create `clients/presentation/router/ClientRouter` with CRUD plus a paginated `find_all` accepting `page`/`size`/`sort`/`direction` query params with bounded ranges
- [ ] 7.3 Create routers for the remaining modules
- [ ] 7.4 Register all routers in `energyhub.main:app` and add a central exception handler mapping domain base exceptions to HTTP status codes (404/409/422)

## 8. API Documentation

- [ ] 8.1 Configure the FastAPI app metadata (`title`, `description`, `version`, `docs_url`, `redoc_url`) in `main.py`
- [ ] 8.2 Add `summary`/`description` to each endpoint and `description` to DTO fields
- [ ] 8.3 Start the app (`poetry run uvicorn energyhub.main:app --reload`) and confirm `/docs` renders every endpoint with request/response schemas

## 9. Validation

- [ ] 9.1 Confirm DTOs, mappers, services, use cases, exceptions, validators, and routers exist for every module
- [ ] 9.2 Exercise create/read/update/delete and a paginated list endpoint end-to-end and verify DTO round-trips
- [ ] 9.3 Verify invalid input and missing/duplicate entities return the expected HTTP error responses
- [ ] 9.4 Run `openspec validate implement-fase-6` and confirm the change is valid
