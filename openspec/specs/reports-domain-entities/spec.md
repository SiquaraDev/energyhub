# reports-domain-entities Specification

## Purpose
TBD - created by archiving change implement-fase-3. Update Purpose after archive.
## Requirements
### Requirement: Report entity creation
The system SHALL create a Report entity in reports/domain/entity/ for generated reports.

#### Scenario: Report entity structure
- **WHEN** the Report entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have report_type field
- **THEN** it SHALL have generated_by field
- **THEN** it SHALL have parameters field
- **THEN** it SHALL have file_path field
- **THEN** it SHALL have status field

