# presentation-layer-base Specification

## Purpose
TBD - created by archiving change implement-fase-2. Update Purpose after archive.
## Requirements
### Requirement: BaseRouter class
The system SHALL create a BaseRouter class in shared/presentation/router/ wrapping FastAPI's APIRouter.

#### Scenario: BaseRouter creation
- **WHEN** the presentation layer is created
- **THEN** the system SHALL create BaseRouter class
- **THEN** BaseRouter SHALL initialize an APIRouter instance in __init__
- **THEN** BaseRouter SHALL provide a get_router method returning the APIRouter

### Requirement: GlobalExceptionHandler
The system SHALL create a global exception handler in shared/presentation/exception/.

#### Scenario: GlobalExceptionHandler creation
- **WHEN** the presentation layer is created
- **THEN** the system SHALL create global_exception_handler async function
- **THEN** the handler SHALL accept Request and Exception parameters
- **THEN** the handler SHALL return a JSONResponse with 500 status code
- **THEN** the response SHALL include timestamp, status, error, message, and path fields

### Requirement: ErrorResponse class
The system SHALL create an ErrorResponse dataclass in shared/presentation/response/.

#### Scenario: ErrorResponse creation
- **WHEN** the presentation layer is created
- **THEN** the system SHALL create ErrorResponse as a dataclass
- **THEN** ErrorResponse SHALL have timestamp field
- **THEN** ErrorResponse SHALL have status field
- **THEN** ErrorResponse SHALL have error field
- **THEN** ErrorResponse SHALL have message field
- **THEN** ErrorResponse SHALL have path field

