## Context

Fase 3 builds upon the architectural structure established in Fase 2 to implement the domain model for the EnergyHub project. The project currently has the Clean Architecture structure with base classes for all layers. This phase focuses on pure domain modeling using Domain-Driven Design principles, creating entities, value objects, enums, and aggregates without any database implementation. The domain layer will be independent of infrastructure concerns.

## Goals / Non-Goals

**Goals:**
- Create all domain entities for the energy trading platform following DDD principles
- Implement relationships between entities using SQLAlchemy relationships (for future ORM mapping)
- Create enums to represent domain states and types
- Create Value Objects for domain concepts with validation logic
- Define aggregates with aggregate roots to enforce consistency boundaries
- Implement business rules and validations using Pydantic field validators
- Create business methods in entities for state transitions
- Create specific domain exceptions for business rule violations

**Non-Goals:**
- No database schema creation or migrations
- No ORM model implementation (only relationships defined)
- No repository implementations
- No use case implementations
- No API endpoints
- No database access or persistence

## Decisions

**Entity Implementation - Python Dataclasses:**
- **Decision:** Use Python dataclasses for domain entities extending BaseEntity
- **Rationale:** Dataclasses provide boilerplate-free classes with type hints, immutability options, and are compatible with Pydantic validation. They are pure Python and don't couple to infrastructure.
- **Alternative considered:** Pydantic models - rejected as they are more suited for DTOs and API models, not domain entities

**Relationships - SQLAlchemy Annotations:**
- **Decision:** Define relationships using SQLAlchemy relationship() with back_populates
- **Rationale:** SQLAlchemy is the chosen ORM for the project. Defining relationships now prepares for future ORM mapping while keeping entities as pure domain objects.
- **Alternative considered:** Pure Python references - rejected as it would require manual relationship management later

**Value Objects - Frozen Dataclasses:**
- **Decision:** Use frozen dataclasses for Value Objects with validation in __post_init__
- **Rationale:** Frozen dataclasses ensure immutability, a key characteristic of Value Objects. Validation on construction guarantees valid values.
- **Alternative considered:** Regular classes - rejected due to lack of immutability guarantee

**Enums - String Enums:**
- **Decision:** Use str, Enum for all domain enums
- **Rationale:** String enums provide readable values that serialize well to JSON and databases. They integrate well with SQLAlchemy and Pydantic.
- **Alternative considered:** Int enums - rejected due to lack of readability and debugging difficulty

**Aggregates - Separate Classes:**
- **Decision:** Create separate aggregate classes that contain the aggregate root and enforce consistency
- **Rationale:** Aggregates represent consistency boundaries. Separate classes allow encapsulation of business rules that span multiple entities.
- **Alternative considered:** Adding methods directly to entities - rejected as it doesn't clearly define aggregate boundaries

**Validation - Pydantic Field Validators:**
- **Decision:** Use Pydantic @field_validator for entity field validation
- **Rationale:** Pydantic provides robust validation with clear error messages. It integrates well with dataclasses and is widely adopted in the Python ecosystem.
- **Alternative considered:** Custom validation methods - rejected due to boilerplate and lack of standardization

**Business Methods - Entity Methods:**
- **Decision:** Implement business methods directly in entities for state transitions
- **Rationale:** Encapsulates business logic within the entity, following DDD principles. State transitions are a core responsibility of the entity.
- **Alternative considered:** Separate service classes - rejected for simple state transitions that belong to the entity

**Domain Exceptions - Specific Hierarchy:**
- **Decision:** Create specific domain exceptions extending DomainException
- **Rationale:** Specific exceptions enable granular error handling and provide clear context about business rule violations.
- **Alternative considered:** Generic exceptions - rejected due to lack of context and handling specificity

## Risks / Trade-offs

**Risk:** SQLAlchemy relationships in domain entities may couple domain to infrastructure
- **Mitigation:** Relationships are defined as forward references and can be removed if needed. The entities remain usable without database access.

**Risk:** Complex validation logic may make entities difficult to maintain
- **Mitigation:** Keep validation focused on single fields. Complex cross-field validation should be in aggregate methods or domain services.

**Risk:** Over-engineering with too many Value Objects
- **Mitigation:** Create Value Objects only for concepts with clear validation rules or business meaning. Start simple and add as needed.

**Trade-off:** Frozen Value Objects vs. flexibility
- **Acceptance:** Immutability is a key Value Object characteristic. If mutation is needed, create a new instance.

**Risk:** Aggregates may become too large and complex
- **Mitigation:** Keep aggregates focused on core consistency boundaries. Extract domain services for complex operations that don't belong in the aggregate.

**Risk:** Business methods in entities may violate single responsibility principle
- **Mitigation:** Only include methods that are core to the entity's identity and state transitions. Extract to domain services for complex operations.
