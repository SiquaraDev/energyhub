## ADDED Requirements

### Requirement: Coverage measurement configuration

The project SHALL configure coverage collection under `[tool.coverage.run]`/`[tool.coverage.report]` in `pyproject.toml`, scoping `source` to the `energyhub` package and omitting non-meaningful paths (tests, `__init__.py`, `main.py`).

#### Scenario: Coverage measures only application code

- **WHEN** the suite runs with coverage enabled
- **THEN** coverage is computed over the `energyhub` package and the omitted paths (tests, package markers, and `main.py`) are excluded from the reported totals

### Requirement: Coverage reporting

The suite SHALL produce both an HTML report (under `htmlcov/`) and a terminal summary so coverage is inspectable locally and in CI output.

#### Scenario: Reports are generated after a coverage run

- **WHEN** `poetry run pytest --cov=energyhub --cov-report=html --cov-report=term` completes
- **THEN** an `htmlcov/index.html` report is written and a per-module coverage summary is printed to the terminal

### Requirement: Enforced minimum coverage gate

The suite SHALL enforce a minimum line coverage of 80% via `--cov-fail-under=80` in the default `addopts` and `fail_under = 80` under `[tool.coverage.report]`, failing the run when coverage drops below the threshold.

#### Scenario: Run fails below the threshold

- **WHEN** total coverage is below 80%
- **THEN** the pytest run exits with a non-zero status and reports the coverage failure

#### Scenario: Run passes at or above the threshold

- **WHEN** total coverage is at least 80%
- **THEN** the coverage gate does not fail the run
