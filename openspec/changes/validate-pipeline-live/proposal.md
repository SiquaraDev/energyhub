## Why

Fase 17 authored the five GitHub Actions workflows (`build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, `ci-cd.yml`) and validated them *locally* — actionlint clean, local `pytest` green, adversarial review — but they have **never executed end-to-end on GitHub-hosted runners**. Local validation cannot exercise the runner OS, real service containers, GHCR authentication with `GITHUB_TOKEN`, the ephemeral kind cluster, or the rollback drill. Until a real run goes green on GitHub, the milestone-1.0.0 claim of "continuously delivered" is unproven and first-run-only breakages (path casing, image visibility, runner RAM, action version drift) remain latent. This change performs the first real run, proves each stage green, and records the evidence.

## What Changes

- Trigger the first real end-to-end pipeline run by pushing to `master`, and confirm the `Build`, `Test`, `Docker`, and combined `CI/CD Pipeline` workflows all complete green on GitHub-hosted `ubuntu-latest` runners.
- Confirm the `Test`/`build-and-test` job provisions Postgres 16 + Redis 7 service containers, applies the Alembic schema, and runs the skip-guarded integration suite against them (not against a dead endpoint).
- Confirm the `Docker` matrix builds and publishes all five service images to GHCR at `ghcr.io/siquaradev/energyhub-<service>` (owner lowercased), each tagged with both `latest` and the commit SHA.
- Confirm the `ci-cd.yml` `deploy` job spins up an ephemeral kind cluster, loads the freshly published images, server-side dry-runs every `k8s/` manifest, applies them, waits on the core stack, and passes the **rollback drill** (bad image → rollout fails → `rollout undo` → recovery).
- Configure the required/optional repository secrets (`CODECOV_TOKEN`, `KUBE_CONFIG`, `SLACK_WEBHOOK_URL`) as needed, **or** confirm the pipeline degrades gracefully without them per the Fase 17 gate-job pattern (missing `KUBE_CONFIG` skips the real deploy cleanly; missing `CODECOV_TOKEN` does not fail the build; missing `SLACK_WEBHOOK_URL` no-ops the notification).
- Capture evidence — workflow run URLs, job logs, the GHCR package listing — fix any first-run breakages that only surface on real runners, and record the verified live pipeline (update `docs/ci-cd.md` and/or add a validation record under the change).

This change modifies **no** workflow behavior by design: the Fase 17 workflows are the artifact under test. Any edits are limited to first-run fixes required to make a real run go green, plus documentation of the verified result.

## Capabilities

### New Capabilities

- `live-pipeline-execution`: The first real end-to-end execution of the `Build`, `Test`, `Docker`, and combined `CI/CD Pipeline` workflows on GitHub-hosted runners, all completing green with correctly ordered stages.
- `ghcr-publication-verification`: Verified publication of all five service images to GHCR under the lowercased `siquaradev` owner, each carrying both the rolling `latest` tag and the immutable commit-SHA tag.
- `ephemeral-deploy-drill-validation`: Verified end-to-end pass of the kind-in-CI deploy stage — image load, server-side manifest dry-run, core-stack readiness, and the injected-failure rollback drill.
- `repository-secret-configuration`: Configuration of the required/optional repository secrets, or confirmation that the pipeline degrades gracefully in their absence following the gate-job pattern.
- `pipeline-validation-record`: Captured first-run evidence (run URLs, logs, package listing), remediation of first-run-only breakages, and a recorded, dated statement that the live pipeline was proven green.

### Modified Capabilities

None — this change validates the Fase 17 capabilities live rather than altering their specified behavior. The existing `build-automation-workflow`, `test-automation-workflow`, `docker-image-build`, `container-registry-publishing`, `kubernetes-deploy-automation`, `deployment-rollback-and-notifications`, and `cicd-pipeline-orchestration` specs remain the source of truth for *what* the workflows do; this change adds specs for *proving they run live*.

## Impact

- **Dependencies**: Fase 17 (all `.github/workflows/*`, `docs/ci-cd.md`, GHCR publishing, kind-in-CI validation) and Fase 16 (the `k8s/` manifests and, for the optional real-cluster path, a reachable cluster behind `KUBE_CONFIG`). No application runtime dependencies change.
- **Consumes**: The five workflows, the per-service `Dockerfile`s (Fase 15), the `k8s/` manifests (Fase 16), the Poetry project and test suite (Fases 1/13), and the GHCR registry.
- **Provides**: A proven-green pipeline, first-run breakage fixes, configured secrets (or documented graceful degradation), and a dated validation record establishing that EnergyHub is genuinely continuously delivered.
- **Operational surface**: GitHub Actions runs consume Actions minutes; GHCR gains five published packages (born private — must be made public or paired with an `imagePullSecret` for any real-cluster pull); repository secrets may be added in repo settings. These are user-driven, one-time steps.
- **Branch/owner**: Default branch is `master`; the GHCR owner/namespace is `siquaradev` (owner `SiquaraDev` lowercased).
- **Artifacts touched**: Possibly `docs/ci-cd.md` (verified-live note) and a validation record; workflow files only if a first-run fix is required. No production code paths change.
