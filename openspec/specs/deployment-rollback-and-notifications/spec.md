# deployment-rollback-and-notifications Specification

## Purpose
TBD - created by archiving change implement-fase-17. Update Purpose after archive.
## Requirements
### Requirement: Readiness gating before completion

The deploy workflow SHALL wait for the deployed workloads to become available (e.g. `kubectl wait --for=condition=available --timeout=300s`) before considering the deployment successful.

#### Scenario: Deployment waits for availability

- **WHEN** manifests are applied
- **THEN** the workflow waits for the target Deployments to reach the `available` condition within the configured timeout before proceeding

#### Scenario: Timeout is treated as failure

- **WHEN** a Deployment does not become available within the timeout
- **THEN** the wait step fails, marking the deployment as failed

### Requirement: Automatic rollback on failure

The deploy workflow SHALL, on failure of the deployment, automatically roll back the affected Deployments to their previous revision using `kubectl rollout undo`.

#### Scenario: Failed deploy is rolled back

- **WHEN** a deployment step fails
- **THEN** a rollback step running with `if: failure()` executes `kubectl rollout undo` for the affected Deployments, restoring the previous working revision

#### Scenario: Successful deploy is not rolled back

- **WHEN** the deployment succeeds
- **THEN** the rollback step does not run

### Requirement: Failure notification

The deploy workflow SHALL send a failure notification (e.g. to Slack) when the deployment fails, so the team is alerted.

#### Scenario: Team is notified on failure

- **WHEN** the deployment fails
- **THEN** a notification step running with `if: failure()` posts a failure message including the job status

