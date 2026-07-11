## ADDED Requirements

### Requirement: Notification entity creation
The system SHALL create a Notification entity in notifications/domain/entity/ for user notifications.

#### Scenario: Notification entity structure
- **WHEN** the Notification entity is created
- **THEN** it SHALL extend BaseEntity
- **THEN** it SHALL have user_id field
- **THEN** it SHALL have title field
- **THEN** it SHALL have message field
- **THEN** it SHALL have status field using NotificationStatus enum
- **THEN** it SHALL have optional user reference
