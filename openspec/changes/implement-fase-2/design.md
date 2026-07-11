## Context

Fase 2 builds upon the infrastructure established in Fase 1 to create the complete architectural structure of the EnergyHub project. The project currently has a basic FastAPI application with Poetry and PostgreSQL configured. This phase implements Clean Architecture and Domain-Driven Design principles by creating the module structure, base classes, and interfaces that will be used throughout the application. The architecture follows the four-layer pattern: Domain, Application, Infrastructure, and Presentation.

## Goals / Non-Goals

**Goals:**
- Create complete module structure following Clean Architecture with 9 modules (shared, auth, clients, contracts, negotiations, financial, audit, notifications, reports)
- Implement base classes for each architectural layer to ensure consistency and reduce code duplication
- Establish interfaces for repositories and use cases that will be implemented by specific modules
- Create shared utilities and constants for cross-module reuse
- Configure CORS and dependency injection in the main application
- Ensure the project runs without errors after architectural changes

**Non-Goals:**
- No business logic implementation in any module
- No database schema creation or migrations
- No API endpoints beyond the existing health check
- No authentication or authorization implementation
- No specific entity or value object definitions

## Decisions

**Module Structure - Clean Architecture:**
- **Decision:** Create 9 modules with 4 layers each (domain, application, infrastructure, presentation)
- **Rationale:** Clean Architecture provides clear separation of concerns, making the codebase maintainable and testable. Each module is independent and can evolve separately.
- **Alternative considered:** Monolithic structure without modules - rejected due to lack of organization and scalability

**Domain Layer Base Classes:**
- **Decision:** Use Python dataclasses for BaseEntity with UUID and timestamp fields
- **Rationale:** Dataclasses provide boilerplate-free classes with type hints and immutability options. UUID ensures unique identifiers across distributed systems.
- **Alternative considered:** ORM models as base classes - rejected as it couples domain to infrastructure

**Repository Pattern:**
- **Decision:** Create abstract Repository interface with generic type parameters
- **Rationale:** Repository pattern abstracts data access, making domain layer independent of persistence implementation. Generics provide type safety and code reuse.
- **Alternative considered:** Direct SQLAlchemy usage in domain - rejected due to coupling domain to infrastructure

**Application Layer Base Classes:**
- **Decision:** Create UseCase interface with generic Input/Output types
- **Rationale:** UseCase pattern encapsulates application logic, making it testable and reusable. Generic types provide flexibility while maintaining type safety.
- **Alternative considered:** Function-based use cases - rejected due to lack of structure and dependency management

**Infrastructure Layer - SQLAlchemy:**
- **Decision:** Create SQLAlchemyRepository base class implementing Repository interface
- **Rationale:** SQLAlchemy provides mature async support and integrates well with PostgreSQL. Base class implements common CRUD operations, reducing duplication.
- **Alternative considered:** Custom ORM implementation - rejected due to complexity and lack of features

**Presentation Layer - FastAPI:**
- **Decision:** Create BaseRouter wrapper around FastAPI's APIRouter
- **Rationale:** Provides consistent router structure and allows for common middleware and exception handling across all modules.
- **Alternative considered:** Direct APIRouter usage - rejected due to lack of consistency

**Exception Handling:**
- **Decision:** Create exception hierarchy (DomainException, ApplicationException) with specific subclasses
- **Rationale:** Structured exception handling enables granular error handling and user-friendly error responses.
- **Alternative considered:** Generic Exception usage - rejected due to lack of context and handling specificity

**Shared Module:**
- **Decision:** Create shared module with util, constant, and enums packages
- **Rationale:** Centralizes common code, prevents duplication, and provides single source of truth for utilities and constants.
- **Alternative considered:** Duplicating code in each module - rejected due to maintenance burden

**CORS Configuration:**
- **Decision:** Configure CORS with permissive settings for development
- **Rationale:** Enables frontend development and API testing. Settings can be tightened for production.
- **Alternative considered:** No CORS configuration - rejected due to frontend integration issues

## Risks / Trade-offs

**Risk:** Deep directory structure may be difficult to navigate
- **Mitigation:** Use IDE navigation features, create clear documentation, and ensure consistent naming conventions

**Risk:** Over-engineering with too many base classes and interfaces
- **Mitigation:** Keep base classes minimal and focused, add complexity only when needed through concrete implementations

**Risk:** Generic types may reduce code readability
- **Mitigation:** Use descriptive type variable names, provide clear documentation, and leverage IDE type hints

**Trade-off:** Additional boilerplate from base classes vs. consistency
- **Acceptance:** The long-term benefits of consistency, type safety, and reduced duplication outweigh initial boilerplate

**Risk:** Module structure may be too granular for a small team
- **Mitigation:** Structure scales well as team grows; modules can be merged if needed without major refactoring
