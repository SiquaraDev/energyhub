## ADDED Requirements

### Requirement: No committed default credential values

The system SHALL NOT ship any default or placeholder credential value in committed source, `docker-compose.yml`, or manifests. The JWT `SECRET_KEY`, the PostgreSQL password, the RabbitMQ password, and the Grafana admin credentials MUST be defined as required configuration with no in-code default, so an unset value is a startup failure rather than a silent insecure default.

#### Scenario: Repository contains no placeholder credentials

- **WHEN** the repository is searched for the known placeholder values (`change-me-in-production`, `energyhub123`, Grafana `admin`/`admin`)
- **THEN** none of them appears as an active credential in source, `docker-compose.yml`, or manifests

#### Scenario: Missing required credential aborts startup

- **WHEN** a service or component starts with a required credential (for example `SECRET_KEY`) unset
- **THEN** it fails to start with a clear configuration error instead of falling back to a default value

### Requirement: Credentials are supplied from environment or secrets

Every rotated credential SHALL be supplied at runtime from an environment variable or a secret reference, and application code and manifests MUST read the value from that source rather than embedding it literally.

#### Scenario: Application reads the JWT key from configuration

- **WHEN** a service constructs its JWT signing configuration
- **THEN** it reads `SECRET_KEY` from its settings, which are populated from an environment variable or secret, not from a literal in code

#### Scenario: Compose and manifests reference injected values

- **WHEN** `docker-compose.yml` or a Kubernetes manifest needs the Postgres, RabbitMQ, or Grafana credential
- **THEN** it references an environment variable or a `Secret` key rather than a hardcoded value

### Requirement: Rotated credentials are fresh and distinct

The rotation SHALL replace each placeholder with a freshly generated, high-entropy value, and the JWT `SECRET_KEY`, the PostgreSQL password, and the RabbitMQ password MUST each be distinct rather than reusing a single shared string.

#### Scenario: Each credential is independently generated

- **WHEN** credentials are rotated for a non-local environment
- **THEN** the `SECRET_KEY`, Postgres password, and RabbitMQ password are distinct high-entropy values, none of which equals a former placeholder

### Requirement: Credential-rotation runbook

The system SHALL provide a documented credential-rotation runbook covering each credential (`SECRET_KEY`, admin login, Grafana, Postgres, RabbitMQ) and the sealed/external-secret workflow, including how to generate a new value, apply it, and back up and restore the sealing or store key.

#### Scenario: Operator rotates a credential using the runbook

- **WHEN** an operator follows the runbook to rotate a given credential
- **THEN** the runbook lists the steps to generate the new value, update the sealed/external secret, and roll the affected services, plus how the sealing or store key is backed up and restored
