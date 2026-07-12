# alembic-configuration Specification

## Purpose
TBD - created by archiving change implement-fase-4. Update Purpose after archive.
## Requirements
### Requirement: Alembic dependency and initialization

The project SHALL include Alembic as a dependency and provide an initialized Alembic environment at the project root, containing `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, and an `alembic/versions/` directory for migration files.

#### Scenario: Alembic environment exists

- **WHEN** a developer inspects the project root after setup
- **THEN** an `alembic.ini` file and an `alembic/` directory with `env.py`, `script.py.mako`, and a `versions/` folder are present

#### Scenario: Alembic command is available

- **WHEN** a developer runs `poetry run alembic --help`
- **THEN** the Alembic CLI executes successfully, confirming the dependency is installed

### Requirement: Migration file naming and timezone

Alembic SHALL be configured to name migration files with a UTC timestamped, human-readable template so migrations sort chronologically and are unambiguous across timezones.

#### Scenario: New migration filename format

- **WHEN** a developer generates a new revision
- **THEN** the created file name includes a UTC date-time prefix, the revision id, and a slug derived from the migration message

### Requirement: Alembic wired to application settings and metadata

The Alembic environment SHALL source the database URL from `settings.database_url` and set `target_metadata` to `Base.metadata`, rather than hard-coding connection details in `alembic.ini`.

#### Scenario: Connection uses application settings

- **WHEN** Alembic runs a migration
- **THEN** it connects using the URL provided by `energyhub.config.settings.database_url`

#### Scenario: Metadata bound for migration context

- **WHEN** the Alembic environment loads
- **THEN** `target_metadata` is set to `energyhub.shared.infrastructure.persistence.database.Base.metadata`

### Requirement: Online and offline migration support

The Alembic environment SHALL support both online (live connection) and offline (SQL script generation) migration modes.

#### Scenario: Online migrations against a live database

- **WHEN** Alembic runs without offline mode
- **THEN** it opens a connection to the configured database and applies migrations transactionally

#### Scenario: Offline migrations emit SQL

- **WHEN** Alembic runs in offline mode
- **THEN** it emits SQL statements using literal bindings instead of connecting to the database

