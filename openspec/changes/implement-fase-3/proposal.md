## Why

The EnergyHub project requires domain entities to represent the business logic and data structures of the energy trading platform. This phase implements Domain-Driven Design principles by creating entities, value objects, enums, and aggregates that encapsulate business rules and ensure data integrity. No database access is implemented yet - this is pure domain modeling.

## What Changes

- Create domain entities for all modules: User, Role, Permission (auth); Client, Contact (clients); Contract (contracts); Negotiation, EnergyTransaction (negotiations); Invoice, Payment (financial); AuditLog (audit); Notification (notifications); Report (reports)
- Define relationships between entities using SQLAlchemy relationships
- Create enums for domain states and types: ContactType, ContractStatus, ContractType, NegotiationStatus, TransactionType, InvoiceStatus, NotificationStatus, AuditAction
- Create Value Objects for domain concepts: CNPJ, Email, Money, PhoneNumber, Address, Percentage
- Create aggregates with aggregate roots: AuthAggregate, ClientAggregate, ContractAggregate, NegotiationAggregate, FinancialAggregate
- Implement domain rules and validations using Pydantic field validators
- Create business methods in entities for state transitions
- Create specific domain exceptions for business rule violations

## Capabilities

### New Capabilities

- `auth-domain-entities`: Creates User, Role, Permission entities with relationships and validations
- `clients-domain-entities`: Creates Client and Contact entities with CNPJ validation and contact types
- `contracts-domain-entities`: Creates Contract entity with status transitions and business rules
- `negotiations-domain-entities`: Creates Negotiation and EnergyTransaction entities
- `financial-domain-entities`: Creates Invoice and Payment entities
- `audit-domain-entities`: Creates AuditLog entity for tracking operations
- `notifications-domain-entities`: Creates Notification entity with status tracking
- `reports-domain-entities`: Creates Report entity for generated reports
- `domain-enums`: Creates enums for all domain states and types
- `domain-value-objects`: Creates Value Objects for CNPJ, Email, Money, PhoneNumber, Address, Percentage
- `domain-aggregates`: Creates aggregates with aggregate roots for consistency boundaries
- `domain-validations`: Implements Pydantic validators and business rules in entities

### Modified Capabilities

None - this is pure domain modeling without database implementation.

## Impact

This phase implements the complete domain model for the EnergyHub platform. No database schema or persistence is implemented yet. The entities use Python dataclasses and will later be mapped to SQLAlchemy ORM models. This provides a pure domain layer that is independent of infrastructure, following DDD principles. All business rules and validations are encapsulated within the domain entities.
