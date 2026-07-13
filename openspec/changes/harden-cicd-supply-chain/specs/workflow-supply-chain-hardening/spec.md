## ADDED Requirements

### Requirement: Least-privilege workflow permissions

Each workflow SHALL declare a least-privilege default `permissions` block (`contents: read`) and SHALL elevate scopes only in the jobs that require them, so no job holds more access than it needs.

#### Scenario: Publish scope is elevated only where needed

- **WHEN** the workflow permissions are inspected
- **THEN** the default token scope is `contents: read` and `packages: write` is granted only to the job that publishes images, while the deploy job that only pulls images holds `packages: read`

#### Scenario: No workflow relies on default broad permissions

- **WHEN** a workflow is read
- **THEN** it declares an explicit `permissions` block rather than inheriting the repository-default token scopes

### Requirement: Concurrency guards cancel superseded runs

Each workflow SHALL declare a `concurrency` group keyed by the workflow and git ref with `cancel-in-progress` enabled, so that a newer push supersedes an in-flight run instead of racing it.

#### Scenario: A newer push cancels the previous run

- **WHEN** a second commit is pushed to the same ref while a workflow run for that ref is still in progress
- **THEN** the earlier run is cancelled and only the run for the newer commit proceeds

### Requirement: Build provenance and SBOM attestation

The image build SHALL enable build provenance and SBOM generation on `docker/build-push-action` (`provenance: true` and `sbom: true`) so each published image carries verifiable origin metadata and a software bill of materials.

#### Scenario: Published image includes provenance and SBOM

- **WHEN** a service image is built and pushed to GHCR
- **THEN** the build attaches a provenance attestation and an SBOM to the published image
