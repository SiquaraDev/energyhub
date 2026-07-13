## ADDED Requirements

### Requirement: Production profile rejects default credential values

When the active profile is `production`, the application SHALL validate at startup that no required credential holds a known default or placeholder value, and it MUST refuse to start if any does.

#### Scenario: Placeholder secret key aborts a production boot

- **WHEN** the application starts with `environment=production` and `SECRET_KEY` still equals `change-me-in-production`
- **THEN** startup fails with an explicit error identifying the offending credential and the process does not begin serving traffic

#### Scenario: Placeholder database or messaging password aborts a production boot

- **WHEN** the application starts with `environment=production` and a database or RabbitMQ credential still equals the placeholder `energyhub123`
- **THEN** startup fails with an explicit error and the process does not begin serving traffic

### Requirement: Production profile rejects empty required credentials

When the active profile is `production`, the application SHALL treat any empty or unset required credential as invalid and MUST refuse to start.

#### Scenario: Empty required credential aborts a production boot

- **WHEN** the application starts with `environment=production` and a required credential is empty or unset
- **THEN** startup fails fast with a configuration error rather than running with a missing credential

### Requirement: Non-production profiles remain permissive

The validation SHALL apply only to the `production` profile, so `development` and `staging`/local profiles continue to start with convenient defaults for local work.

#### Scenario: Development boot is unaffected by the guard

- **WHEN** the application starts with `environment=development` and a credential still holds a development default
- **THEN** startup proceeds normally and the production guard does not trigger
