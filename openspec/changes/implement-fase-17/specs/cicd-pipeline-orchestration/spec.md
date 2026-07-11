## ADDED Requirements

### Requirement: End-to-end pipeline with staged jobs

The system SHALL provide a combined GitHub Actions pipeline (e.g. `.github/workflows/ci-cd.yml`) that orchestrates the full delivery flow as staged jobs: build-and-test, build-and-push, and deploy.

#### Scenario: Pipeline defines the three stages

- **WHEN** the combined pipeline runs
- **THEN** it contains a build-and-test job, a build-and-push job, and a deploy job covering the full delivery flow

### Requirement: Ordered execution via job dependencies

The pipeline SHALL enforce ordering through job `needs` dependencies so that images are only pushed after build-and-test succeeds and deployment only runs after images are pushed.

#### Scenario: Later stages depend on earlier ones

- **WHEN** the pipeline executes
- **THEN** `build-and-push` runs only after `build-and-test` succeeds, and `deploy` runs only after `build-and-push` succeeds

#### Scenario: A failed stage stops the pipeline

- **WHEN** the build-and-test stage fails
- **THEN** the downstream `build-and-push` and `deploy` jobs do not run

### Requirement: Pipeline documentation

The change SHALL document the CI/CD pipeline in `docs/ci-cd.md`, describing the workflows, required secrets, and the deploy/rollback flow.

#### Scenario: Documentation describes the pipeline

- **WHEN** a developer reads `docs/ci-cd.md`
- **THEN** they can identify each workflow, the secrets it requires, and how deployment and rollback behave
