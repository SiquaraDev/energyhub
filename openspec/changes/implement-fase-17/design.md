## Context

The platform is fully built and containerized: Fase 1 established the Poetry project, Fase 13 the test suites, Fase 15 the per-service `Dockerfile`s, and Fase 16 the `k8s/` manifests. What is missing is automation — today build, test, image publish, and deploy are manual, so releases are slow, unverified, and inconsistent. This final phase adds GitHub Actions pipelines to close that gap.

The constraints are fixed by earlier phases: Python 3.12 + Poetry, one image per service under `services/<service>/`, and a Kubernetes cluster whose desired state lives in `k8s/`. CI/CD is configuration (YAML workflows) plus a small amount of documentation; it introduces no application runtime code and no schema changes. It does introduce an operational surface — secrets, a live cluster, and an external registry — that must be handled safely.

## Goals / Non-Goals

**Goals:**
- Automate build + test on every push/PR, gating merges on a green suite with coverage reporting.
- Run integration tests against real Postgres/Redis service containers in CI.
- Build one Docker image per service via a Buildx matrix with layer caching.
- Publish images to a container registry tagged with `latest` and the commit SHA.
- Deploy to Kubernetes automatically on `main`, verify rollout, and roll back on failure with a notification.
- Orchestrate the full flow (build/test → push → deploy) as a single ordered pipeline and document it.

**Non-Goals:**
- No changes to application code, `Dockerfile`s, or `k8s/` manifests (owned by Fases 15/16).
- No multi-environment promotion (staging → prod), blue/green, or canary strategy — single-target deploy on `main`.
- No infrastructure provisioning (cluster, registry, DNS) — those are assumed to exist.
- No secret-management platform (Vault/SOPS); secrets are stored as GitHub repository secrets.

## Decisions

**Separate, single-purpose workflows plus one orchestrator:**
- **Decision:** Author focused workflows (`build.yml`, `test.yml`, `docker.yml`, `deploy.yml`) and one combined `ci-cd.yml` that chains build/test → push → deploy via job `needs`.
- **Rationale:** Small workflows are easy to reason about, re-run, and trigger on different events; the orchestrator gives an end-to-end gated path for `main` without duplicating logic conceptually. This mirrors the phase plan, which introduces each workflow independently then a combined pipeline.
- **Alternative considered:** A single monolithic workflow with all jobs — rejected because it couples unrelated triggers (feature-branch tests vs. main-only deploy) and makes partial re-runs awkward.

**Integration tests run against service containers, not mocks:**
- **Decision:** Provision Postgres and Redis as GitHub Actions `services` with health checks, and pass `DATABASE_URL`/`REDIS_URL` to the integration step.
- **Rationale:** The persistence and cache layers were specified against real backends; testing against containers catches driver/SQL/serialization issues that mocks hide. Health checks ensure tests start only when services are ready.
- **Alternative considered:** In-memory/SQLite substitutes or mocked clients — rejected because async Postgres (asyncpg) behavior and Redis semantics differ enough to give false confidence.

**Immutable SHA tags alongside a rolling `latest`:**
- **Decision:** Push each image as both `:latest` and `:${{ github.sha }}`.
- **Rationale:** The SHA tag is immutable and traceable — any running pod can be tied back to an exact commit — while `latest` remains a convenient rolling pointer. This is the tagging scheme the plan specifies.
- **Alternative considered:** Only `latest` — rejected as untraceable and unsafe for rollbacks; semantic version tags — deferred, since the project has no release-versioning process yet.

**Registry target selected by configuration, not code:**
- **Decision:** Keep the build/tag/push structure constant and switch only the login step and secrets to target Docker Hub or AWS ECR.
- **Rationale:** Teams differ on registry choice; isolating the difference to authentication keeps the pipeline portable and avoids forking the build logic.
- **Alternative considered:** Hard-coding Docker Hub — rejected because the plan explicitly documents an ECR path as an alternative.

**Deploy verifies rollout and self-heals via rollback:**
- **Decision:** After `kubectl apply`, gate on `kubectl wait`/`rollout status`; on failure run `kubectl rollout undo` (`if: failure()`) and post a Slack notification.
- **Rationale:** A deploy that leaves the cluster in a broken state is worse than no deploy; automatic rollback restores the last good revision and the notification makes the failure visible immediately.
- **Alternative considered:** Deploy-and-forget with manual rollback — rejected as slow to detect and recover; full GitOps (Argo CD/Flux) — deferred as a larger architectural change beyond this phase's scope.

**Secrets via GitHub repository secrets:**
- **Decision:** Store `DOCKER_USERNAME`/`DOCKER_PASSWORD` (or ECR/AWS credentials) and `KUBE_CONFIG` as GitHub secrets referenced in workflows; never commit credentials.
- **Rationale:** It is the native, lowest-friction mechanism for Actions and keeps the repository free of sensitive material.
- **Alternative considered:** A dedicated secret manager (Vault, SOPS-encrypted files) — deferred; unnecessary complexity for the current single-repo, single-cluster setup.

## Risks / Trade-offs

- **Leaked secrets** (kubeconfig, registry, cloud credentials) → Store only as GitHub secrets, never echo them, scope tokens to least privilege, and prefer short-lived ECR/OIDC auth where available.
- **`latest`-based deploys are ambiguous** → Deploy manifests should reference the SHA tag (or be updated to it) for reproducibility; `latest` alone can deploy an unexpected image. Documented in `docs/ci-cd.md` as the recommended practice.
- **Auto-rollback can mask a real defect** → Rollback restores availability but the failing change must still be investigated; the failure notification and retained logs/artifacts ensure the failure is not silently swallowed.
- **Flaky integration tests block delivery** → Health-check the service containers before running tests and keep tests isolated; upload results with `if: always()` so failures are diagnosable rather than opaque.
- **Cache poisoning / stale layers** → Registry-backed Buildx cache is keyed per service; a corrupt cache is recoverable by invalidating the `:build` cache ref.
- **Cluster/registry unavailable at deploy time** → The rollout-status/`wait` gate surfaces the failure and triggers rollback + notification rather than leaving a half-applied state.
- **Workflows cannot be fully validated without live infrastructure** → Since application code and infra are not materialized, workflows are authored to the plan and validated for syntax; end-to-end validation happens once secrets and the cluster are wired.

## Migration Plan

1. Add `.github/workflows/build.yml`; push and confirm it builds, tests, and reports coverage.
2. Add `test.yml` with Postgres/Redis service containers; confirm unit and integration suites run against them.
3. Add `docker.yml` (Buildx matrix + caching) and configure registry secrets; confirm all service images build.
4. Enable publishing (login + `latest`/SHA tags); confirm images appear in the registry.
5. Add `deploy.yml` with the `KUBE_CONFIG` secret; confirm `kubectl apply` and rollout verification against the cluster.
6. Add readiness gating, `rollout undo` on failure, and the Slack notification; test by intentionally deploying a broken revision and confirming rollback + alert.
7. Add the combined `ci-cd.yml` with `needs` ordering; push to `main` and confirm the staged run end to end.
8. Document the pipeline in `docs/ci-cd.md`.
9. Rollback of the change itself: workflows are additive config files; deleting `.github/workflows/*` disables automation without affecting the running cluster.

## Open Questions

- Should deploy manifests be pinned to the commit-SHA image tag automatically (image substitution) instead of relying on `latest`? (Recommended, but requires a manifest-templating step to be decided when endpoints/manifests are finalized.)
- Which registry is the canonical target — Docker Hub or AWS ECR — and should ECR auth move to OIDC role assumption rather than static access keys?
- Should the pipeline promote through environments (e.g. `develop` → staging, `main` → production) in a later iteration, or remain single-target for now?
- What branch protection rules should require the build/test workflows to pass before merge (enforced in repository settings, outside the workflow files)?
