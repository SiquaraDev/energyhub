## Context

Fase 17 delivered five GitHub Actions workflows and documented them in `docs/ci-cd.md`, closing the roadmap at `1.0.0`. Their entire validation was **local**: `actionlint` for syntax, a local `pytest` run for the test steps, and an adversarial read-through of each workflow. That is necessary but not sufficient — a workflow can be syntactically perfect and still fail the first time a real runner executes it. The things local validation cannot exercise are exactly the things that break first runs: the `ubuntu-latest` filesystem and casing, GHCR authentication with the ambient `GITHUB_TOKEN`, service-container networking, disk pressure on the runner, the ephemeral kind cluster, action major-version resolution, and package visibility defaults.

The current state is therefore: the pipeline *exists* and is *believed* correct, but "continuously delivered" is an unproven claim. This change is operational — its deliverable is a **proven-green live run plus recorded evidence**, not new pipeline behavior. The workflows are the system under test. The constraints are inherited and fixed: default branch `master`; GHCR owner `siquaradev` (from `SiquaraDev`, lowercased for OCI refs); the five services with `Dockerfile`s (`auth`, `client`, `contract`, `financial`, `audit`); Traefik as the gateway (no built image); the free ephemeral-kind deploy validation in `ci-cd.yml`; and a real-cluster deploy (`deploy.yml`) that stays cleanly skipped until `KUBE_CONFIG` is provided.

Some steps are inherently **user-driven** and cannot be performed by an automated agent: pushing to `master`, adding repository secrets in GitHub settings, and changing GHCR package visibility. This design describes those as explicit, verifiable tasks and treats their evidence (run URLs, screenshots, `gh` output) as the acceptance artifact.

## Goals / Non-Goals

**Goals:**
- Execute the first real end-to-end run of `Build`, `Test`, `Docker`, and the combined `CI/CD Pipeline` on GitHub-hosted runners and confirm each is green.
- Prove the test stage runs the skip-guarded integration suite against real Postgres/Redis service containers (schema applied via Alembic), not against a dead endpoint.
- Prove all five images publish to `ghcr.io/siquaradev/energyhub-<service>` with both `latest` and the commit-SHA tag.
- Prove the ephemeral-kind `deploy` stage passes end to end, including the injected-failure rollback drill.
- Configure the required/optional secrets, or confirm and document graceful degradation without them.
- Capture evidence, remediate first-run-only breakages, and record the verified pipeline.

**Non-Goals:**
- No change to *what* the workflows do — the Fase 17 specs remain authoritative; edits are limited to first-run fixes needed to go green.
- No standing/24-7 real cluster: the free ephemeral-kind path is the proof of the deploy mechanism; a real `KUBE_CONFIG` deploy is optional and out of scope to *stand up* here.
- No multi-environment promotion, blue/green, canary, GitOps, or branch-protection policy authoring — those remain deferred from Fase 17.
- No secret-management platform; secrets stay as GitHub repository secrets.
- No re-validation of the full ~17-pod stack in CI — the runner deliberately gates a core subset (the full stack was validated live on minikube in Fase 16).

## Decisions

**Prove the whole pipeline in a single push to `master`:**
- **Decision:** Trigger `build.yml`, `test.yml`, `docker.yml`, and `ci-cd.yml` together with one push to `master` (all four are triggered by `push` to `main`/`master`), and evaluate each run independently.
- **Rationale:** A single push reproduces the real developer flow and surfaces cross-workflow interactions (e.g. `docker.yml` and `ci-cd.yml`'s `build-and-push` both publishing the same SHA tags concurrently) that per-workflow `workflow_dispatch` runs would hide. Evidence is one commit SHA tying every run and every image together.
- **Alternative considered:** Manually dispatching each workflow in isolation — rejected because it does not reproduce the concurrent-publish reality and fragments the evidence trail across unrelated SHAs.

**The ephemeral-kind stage is the canonical proof of deploy + rollback:**
- **Decision:** Treat `ci-cd.yml`'s `deploy` job (kind on the runner) as the acceptance path for the deploy and rollback capabilities, and treat `deploy.yml` (real cluster) as an optional, separately-gated path proven only if `KUBE_CONFIG` is supplied.
- **Rationale:** The ephemeral path needs no external infrastructure, runs green for free on every push, and exercises the real mechanism — image load, server-side dry-run of all manifests, core-stack readiness, and `rollout undo` recovery. Requiring a standing cluster would make "green" depend on infra that may not exist.
- **Alternative considered:** Gating acceptance on a real `KUBE_CONFIG` deploy — rejected as it couples the milestone to provisioning a cluster that Fase 17 intentionally left optional.

**Accept graceful degradation as a first-class, verifiable outcome for optional secrets:**
- **Decision:** For `CODECOV_TOKEN`, `KUBE_CONFIG`, and `SLACK_WEBHOOK_URL`, either configure the secret *or* record that the pipeline stays green without it — the Codecov upload does not fail the build (`fail_ci_if_error: false`), the `deploy.yml` gate job skips the real deploy cleanly, and the Slack step no-ops when the webhook is absent.
- **Rationale:** Fase 17 engineered the pipeline to work out-of-the-box with only the ambient `GITHUB_TOKEN`; validation must *prove* that property rather than assume it. "Degrades gracefully" is a testable claim (the run is green, the skipped/soft-failed step is visible in logs).
- **Alternative considered:** Making all secrets mandatory before declaring success — rejected as it contradicts the deliberate out-of-the-box design and would block validation on external accounts.

**Make GHCR packages pullable for the deploy stage, deliberately and minimally:**
- **Decision:** After first publish, confirm the `deploy` job can pull the SHA-tagged images; since it authenticates to GHCR with `GITHUB_TOKEN` in the same repo, private packages are pullable in-workflow. Only if a *real* external cluster is wired do we make packages public or add an `imagePullSecret`.
- **Rationale:** New GHCR packages are born private; the in-CI `docker/login-action` step already handles that for the ephemeral kind load, so no visibility change is required to prove the pipeline. Visibility changes are reserved for the real-cluster path and flagged as a security-relevant, user-driven action.
- **Alternative considered:** Flipping all packages public immediately — rejected as an unnecessary exposure that the in-CI login makes moot for the validated path.

**Fix-forward on first-run breakages, in the workflow, not by loosening specs:**
- **Decision:** When a real run reveals a breakage (e.g. action major-version drift, casing, runner disk/RAM, image-publish race in `deploy.yml`'s wait loop), fix the workflow minimally and re-run until green; do not weaken acceptance criteria to match a red run.
- **Rationale:** The point of the exercise is a genuinely green pipeline. First-run fixes are expected and are the concrete value of running live; the specs describe the target state and stay fixed.
- **Alternative considered:** Recording "known failures" and declaring partial success — rejected as it defeats the purpose of proving continuous delivery.

**Record evidence as durable, linkable proof:**
- **Decision:** Capture the run URLs, the resolved commit SHA, the GHCR package listing (`latest` + SHA tags per service), and the rollback-drill log excerpt; then annotate `docs/ci-cd.md` with a dated "verified live" note and/or add a validation record under the change directory.
- **Rationale:** A green run is ephemeral in memory but the milestone claim must be auditable later; a recorded, dated artifact with links is the durable proof.
- **Alternative considered:** Relying on the Actions history alone — rejected because run retention and log expiry make it a weak long-term record; a committed note is durable.

## Risks / Trade-offs

- **First-run-only breakages surface on real runners** (casing, action major-version resolution, disk/RAM pressure) → Expected; fix-forward minimally in the workflow and re-run until green, capturing each fix in the evidence trail.
- **GHCR packages born private block a real cluster pull** → The in-CI `deploy` job logs in with `GITHUB_TOKEN`, so the validated ephemeral path is unaffected; visibility change or `imagePullSecret` is required only for the optional real-cluster path and is flagged as user-driven and security-relevant.
- **Concurrent publish race** — `docker.yml` and `ci-cd.yml`'s `build-and-push` push the same SHA tags on the same push → Both are idempotent overwrites of identical content; if `deploy.yml`'s SHA-wait loop times out, its 20×15s retry (already in the workflow) absorbs publish latency.
- **Runner RAM cannot hold the full stack** → The `deploy` job intentionally scales services to 1 replica and gates only the core subset (Postgres/Redis/RabbitMQ/Consul + auth/client); Kafka/Zookeeper are applied but not awaited. The drill proves the *mechanism*, not full-stack capacity.
- **Rollback drill false-negative** — an inexistent image might be mis-read as a slow pull → The drill asserts the rollout does **not** complete within the timeout, then `rollout undo`, then asserts recovery; both the failure and the recovery are explicit `rollout status` checks, not inferred.
- **Optional secrets absent make "green" ambiguous** → Acceptance requires the *specific* degraded behavior to be visible in logs (Codecov soft-fail, deploy gate skip, Slack no-op), so a green run without secrets is a positive result, not an untested gap.
- **Actions minutes / cost** → Bounded: validation is a small number of pushes; the ephemeral kind path needs no paid infrastructure.
- **User-driven steps cannot be automated** → Pushing, adding secrets, and changing package visibility are described as explicit tasks with evidence requirements; they are left unchecked for the human operator to perform and confirm.

## Migration Plan

1. Pre-flight: confirm the five workflows and `docs/ci-cd.md` are present on `master` and that `actionlint` is still clean locally.
2. Decide the secret posture — either add `CODECOV_TOKEN` / `KUBE_CONFIG` / `SLACK_WEBHOOK_URL` in repo settings, or explicitly validate the out-of-the-box (secretless) path.
3. Push to `master`; watch `Build`, `Test`, `Docker`, and `CI/CD Pipeline` runs.
4. Triage any red run, apply a minimal first-run fix in the affected workflow, and re-push until all four are green.
5. Confirm GHCR shows five `energyhub-<service>` packages, each with `latest` and the SHA tag.
6. Confirm the `deploy` job (kind) passes: image load, dry-run, core readiness, and the rollback drill recovery.
7. If validating graceful degradation, confirm the degraded steps behaved as designed (Codecov soft-fail, deploy gate skip, Slack no-op).
8. Optionally, wire `KUBE_CONFIG` and prove the real-cluster `deploy.yml` path (make packages public or add an `imagePullSecret` first).
9. Capture evidence and record the verified pipeline in `docs/ci-cd.md` and/or a validation record.
10. Rollback of *this* change: it adds evidence/notes and at most minimal workflow fixes; reverting the note/fixes returns to the prior state without affecting any running cluster.

## Open Questions

- Should the milestone additionally require the real-cluster `deploy.yml` path (behind `KUBE_CONFIG`) to be proven, or is the ephemeral-kind proof sufficient for `1.0.0`? (This design treats ephemeral-kind as sufficient and the real path as optional.)
- Should the GHCR packages be made public as a standing decision (simpler pulls, wider exposure) or kept private with an `imagePullSecret` for any real cluster?
- Where should the durable evidence live long-term — inline in `docs/ci-cd.md`, a dedicated `docs/validation/` record, or the archived change folder — given Actions log retention expires?
- Should branch protection be configured to *require* the `Build`/`Test` runs to pass before merge to `master` as a follow-up, now that the runs are proven green? (Repository-settings change, outside the workflow files.)
