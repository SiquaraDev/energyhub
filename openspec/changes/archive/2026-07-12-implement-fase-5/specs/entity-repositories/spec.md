## ADDED Requirements

### Requirement: One repository per domain entity

The system SHALL provide a concrete repository for each domain entity — `UserRepository`, `RoleRepository`, `PermissionRepository`, `ClientRepository`, `ContactRepository`, `ContractRepository`, `NegotiationRepository`, `EnergyTransactionRepository`, `InvoiceRepository`, `PaymentRepository`, `AuditLogRepository`, `NotificationRepository`, and `ReportRepository` — each extending the generic repository base.

#### Scenario: Repository placement follows module boundaries

- **WHEN** a repository is created for a module
- **THEN** it lives under that module's `infrastructure/persistence/` package and extends `SQLAlchemyRepository`

### Requirement: Auth finder methods

`UserRepository` SHALL provide `find_by_username`, `find_by_email`, `exists_by_username`, `exists_by_email`, and `find_by_role_name`. `RoleRepository` and `PermissionRepository` SHALL provide `find_by_name` and `exists_by_name`.

#### Scenario: Lookup by unique business key

- **WHEN** `find_by_username` is called with an existing username
- **THEN** the matching `User` is returned, and `None` is returned when no user has that username

#### Scenario: Existence checks for uniqueness validation

- **WHEN** `exists_by_email` is called with an email already in use
- **THEN** it returns `True`, enabling duplicate-prevention before insert

### Requirement: Client and contact finder methods

`ClientRepository` SHALL provide `find_by_cnpj`, `exists_by_cnpj`, `find_by_active_true`, `search_by_name`, and `find_by_location`. `ContactRepository` SHALL provide `find_by_client_id` and `find_by_client_id_and_type`.

#### Scenario: Case-insensitive name search

- **WHEN** `search_by_name` is called with a partial term
- **THEN** clients whose corporate name or trade name contains that term (case-insensitive) are returned

#### Scenario: Contacts scoped to a client

- **WHEN** `find_by_client_id` is called
- **THEN** only the contacts belonging to that client are returned

### Requirement: Finder methods for remaining entities

The remaining repositories (`ContractRepository`, `NegotiationRepository`, `EnergyTransactionRepository`, `InvoiceRepository`, `PaymentRepository`, `AuditLogRepository`, `NotificationRepository`, `ReportRepository`) SHALL expose the entity-specific lookup methods their domain requires (e.g. lookup by business number, by owning entity id, or by status).

#### Scenario: Lookup by owning entity

- **WHEN** a contract-scoped repository method is called with a `client_id`
- **THEN** only records associated with that client are returned
