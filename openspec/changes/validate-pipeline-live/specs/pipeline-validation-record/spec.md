## ADDED Requirements

### Requirement: First-run evidence is captured

The change SHALL capture durable evidence of the live run: the workflow run URLs, the validated commit SHA, the GHCR package listing showing `latest` and SHA tags per service, and a log excerpt of the rollback-drill recovery.

#### Scenario: Evidence set is collected

- **WHEN** the live pipeline has run green
- **THEN** the run URLs, commit SHA, GHCR package/tag listing, and rollback-drill recovery log excerpt are collected as evidence

### Requirement: First-run-only breakages are remediated

Any breakage that surfaces only on a real runner (for example action major-version drift, path casing, runner disk/RAM pressure, or an image-publish race) SHALL be fixed minimally in the affected workflow and the pipeline re-run until green, without weakening the acceptance criteria.

#### Scenario: A red first run is fixed forward to green

- **WHEN** the first live run fails on a runner-only issue
- **THEN** a minimal fix is applied to the affected workflow and the pipeline is re-run until all four workflows conclude green

#### Scenario: Acceptance criteria are not loosened to match a red run

- **WHEN** remediating a first-run breakage
- **THEN** the fix changes the workflow to make a genuinely green run, and does not relax any validation requirement to accept a red run

### Requirement: The verified pipeline is recorded durably

The change SHALL record the verified-live result durably — a dated note in `docs/ci-cd.md` and/or a validation record — so the green-pipeline claim is auditable after Actions log retention expires.

#### Scenario: A dated verified-live record exists

- **WHEN** validation is complete
- **THEN** a dated record (in `docs/ci-cd.md` and/or a validation record) states that the pipeline ran green live, references the evidence, and identifies the validated commit SHA
