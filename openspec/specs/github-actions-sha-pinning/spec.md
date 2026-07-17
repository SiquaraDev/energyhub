# github-actions-sha-pinning Specification

## Purpose
TBD - created by archiving change harden-cicd-supply-chain. Update Purpose after archive.
## Requirements
### Requirement: Actions pinned to immutable commit SHAs

Every third-party GitHub Actions `uses:` reference in the workflows under `.github/workflows/` SHALL be pinned to a full 40-character commit SHA rather than a mutable tag or branch (e.g. `@v7`, `@v1`, `@main`), so that a compromised or repointed upstream tag cannot silently change the code the pipeline executes.

#### Scenario: Every action reference resolves to a commit SHA

- **WHEN** the `uses:` references across `build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, and `ci-cd.yml` are enumerated
- **THEN** each one references a full 40-character commit SHA and none references a mutable tag or branch

#### Scenario: All in-use actions are covered

- **WHEN** the set of distinct actions is collected (`actions/checkout`, `actions/setup-python`, `snok/install-poetry`, `actions/cache`, `codecov/codecov-action`, `actions/upload-artifact`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/build-push-action`, `azure/k8s-set-context`, `slackapi/slack-github-action`, `helm/kind-action`)
- **THEN** every one of them is pinned to a commit SHA in all workflows where it appears

### Requirement: Human-readable version comment on each pin

Each pinned `uses:` reference SHALL carry a trailing comment stating the human-readable release the SHA corresponds to (e.g. `# v7`), so that a reader can identify the version without resolving the SHA.

#### Scenario: Pin includes a version comment

- **WHEN** a pinned action reference is read
- **THEN** it is followed by a comment naming the release tag that the pinned commit SHA belongs to

### Requirement: Automated pin updates via Dependabot

The repository SHALL include a Dependabot configuration (`.github/dependabot.yml`) enabling the `github-actions` package ecosystem so that updates to the pinned SHAs are proposed as reviewable pull requests on a schedule.

#### Scenario: Dependabot proposes a SHA bump

- **WHEN** an upstream action publishes a newer release than a currently pinned commit
- **THEN** Dependabot opens a pull request that updates the pinned SHA and its version comment for review

#### Scenario: Configuration targets the actions ecosystem

- **WHEN** `.github/dependabot.yml` is inspected
- **THEN** it declares a `package-ecosystem: "github-actions"` entry covering the workflow directory

