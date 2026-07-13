## Context

Fase 17 (milestone 1.0.0) delivered five GitHub Actions workflows in `.github/workflows/` — `build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, and the combined `ci-cd.yml` — that build the Poetry monolith, run the test suite against Postgres/Redis service containers, build one image per service via a Buildx matrix, publish those images to GHCR (`ghcr.io/<owner>/energyhub-<service>`), and deploy to Kubernetes with rollout verification and rollback. The pipeline works, but three supply-chain gaps remain:

1. **Mutable action pins.** All 13 distinct actions are referenced by moving tags (`@v7`, `@v6`, `@v5`, `@v4`, `@v2`, `@v1`). A moving tag can be repointed by a compromised or hijacked upstream to run arbitrary code with the workflow token's privileges — the well-known `tj-actions`-style supply-chain risk.
2. **Unprotected default branch.** `master` (the default) has no required status checks, no required review, and permits direct pushes, so unverified or unreviewed code can land and immediately trigger publish/deploy.
3. **Private-by-default images.** GHCR packages are created private. The Fase 17 `ci-cd.yml` deploy job sidesteps this by running against an ephemeral in-runner `kind` cluster and `docker login`-ing before `kind load`; a real external cluster has no such login and cannot pull the images without an explicit pull secret.

The constraints are inherited from earlier phases: the workflows operate in `energyhub/` for the monolith build, the GHCR owner ref must be lowercased (`siquaradev`), the default branch is `master` (workflows already also honor `main`), and the Fase 16 Deployments in `k8s/` currently reference local image names (`energyhub-<svc>-service:latest`, `imagePullPolicy: IfNotPresent`) with no ServiceAccount or `imagePullSecrets`. This change is configuration and manifest hardening — it introduces no application runtime code and no schema changes — but it touches an operational surface (repository settings, registry visibility, cluster secrets) that must be handled without leaking credentials.

## Goals / Non-Goals

**Goals:**
- Make every action reference immutable by pinning to a full commit SHA, with a version comment, and keep the pins fresh via Dependabot.
- Enforce branch protection on `master`/`main`: no direct pushes, required review, and required build/test status checks — captured reproducibly.
- Let a real cluster pull the private GHCR images via a `dockerconfigjson` pull secret wired into the service workloads, with a public-package alternative documented.
- Tighten the operational surface: least-privilege `permissions`, concurrency guards, and provenance/SBOM attestation on published images.

**Non-Goals:**
- No changes to what the pipeline builds, tests, publishes, or deploys — the Fase 17 behavior (matrix, tags, rollout/rollback) is preserved, only hardened.
- No new registry (stays on GHCR), no migration to an OIDC/keyless signing platform (cosign/Sigstore) beyond the build-in provenance/SBOM — that is a larger follow-up.
- No secret-management platform (Vault/SOPS/External Secrets); the pull secret is materialized from a GitHub-provided token.
- No enforcement of branch protection from within the workflow YAML — GitHub does not allow that; it remains a repository setting captured as a script.

## Decisions

**Pin to commit SHAs with a version comment, not to tags:**
- **Decision:** Rewrite every `uses: <action>@<tag>` to `uses: <action>@<40-char-sha> # <tag>`, resolving each SHA from the exact commit the current tag points to at pinning time.
- **Rationale:** The SHA is immutable — an upstream cannot repoint it — which closes the tag-hijack vector while the trailing comment preserves human readability. This is GitHub's own hardening guidance for third-party actions.
- **Alternative considered:** Trusting major-version tags (`@v7`) — rejected, because tags are mutable and the whole point is to remove that trust. A vendored/forked copy of each action — rejected as high-maintenance overkill for 13 well-known actions.

**Adopt Dependabot for the `github-actions` ecosystem:**
- **Decision:** Add `.github/dependabot.yml` with a `github-actions` entry so SHA pins get reviewable bump PRs on a schedule.
- **Rationale:** SHA pins are safe but go stale (missing security fixes). Dependabot bumps the SHA and the version comment together, turning "pin and forget" into "pin and review", keeping immutability without freezing.
- **Alternative considered:** Manual periodic re-pinning — rejected as unreliable; a third-party pinning bot (e.g. `pin-github-action`) — deferred, Dependabot is native and sufficient.

**Branch protection as a committed `gh api` script plus documentation, not clicked settings:**
- **Decision:** Encode the required rules (dismiss-stale-reviews off is acceptable; require ≥1 approval; require the `build` and `test` checks; block direct pushes) as a reproducible `gh api` script under `.github/`/`docs/`, and align workflow job/check names so the required checks resolve. Cover both `master` and `main`.
- **Rationale:** Protection lives outside the workflow files and cannot be expressed in YAML; capturing it as code makes it auditable, reviewable, and re-appliable, and documents the human step a repo admin must run.
- **Alternative considered:** Documentation-only ("go set these toggles") — rejected as drift-prone and unverifiable; a full IaC provider (Terraform GitHub provider) — deferred as heavier than this single-repo change warrants.

**Private images + `dockerconfigjson` pull secret as the primary path; public packages documented as the alternative:**
- **Decision:** Create a `kubernetes.io/dockerconfigjson` secret for `ghcr.io` in the `energyhub` namespace and wire it into the service pods via the namespace ServiceAccount (and/or each Deployment's `imagePullSecrets`). Document making the packages public as the simpler alternative for environments that accept world-readable images.
- **Rationale:** A pull secret keeps the images private while still cluster-pullable — the safer default for a production-shaped platform — and wiring it on the ServiceAccount covers all pods in the namespace with one reference. Publishing public removes the secret entirely but exposes the images; offering both lets the operator choose per environment.
- **Alternative considered:** Only making packages public — rejected as the default because it discards access control; per-pod inline `.dockerconfigjson` — rejected as duplicative versus a single namespaced secret.

**Least-privilege permissions, concurrency guards, and provenance/SBOM as incremental hardening:**
- **Decision:** Keep the existing default `permissions: contents: read`, elevate `packages: write` only in the publish job and `packages: read` in the deploy job; add a `concurrency` group per workflow keyed by `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`; set `provenance: true` and `sbom: true` on `docker/build-push-action`.
- **Rationale:** These are low-risk, high-value tightenings — least privilege limits blast radius if a step is compromised, concurrency stops superseded runs from racing (and wasting minutes / double-deploying), and provenance/SBOM give the published images verifiable origin and a component inventory.
- **Alternative considered:** Full cosign keyless signing and attestation verification at deploy — deferred; the build-in `provenance`/`sbom` flags deliver most of the value with none of the key-management overhead.

## Risks / Trade-offs

- **A pinned SHA goes stale and misses a security fix** → Dependabot opens bump PRs so pins are refreshed under review rather than frozen; the version comment keeps each pin auditable at a glance.
- **Pinning the wrong SHA (typo, or a tag that was itself moved before pinning)** → Resolve each SHA from the upstream release/tag at pinning time and record the version in the comment; the workflows still run in CI, so a bad pin surfaces as a failed run, not a silent compromise.
- **Branch protection can lock out automation or admins** → Scope required checks to the `build` and `test` workflows only (not deploy, which needs `main`/`master` context), allow admins where necessary, and keep the `gh api` script in-repo so the rules can be adjusted and re-applied deliberately.
- **The `dockerconfigjson` token is a leak vector** → Build it from the workflow `GITHUB_TOKEN` or a narrowly-scoped `read:packages` PAT, store it only as a Kubernetes/GitHub secret, never commit it, and prefer the ServiceAccount wiring so it lives in one place.
- **Provenance/SBOM changes the build output and could break the matrix** → The flags are additive on `docker/build-push-action`; validate one service builds green before rolling across the matrix, and they do not alter the image tags the deploy relies on.
- **Required status-check names can drift if workflow job names change** → Freeze the check names referenced by branch protection and treat renames as a coordinated change to both the workflow and the protection script.
- **Cannot fully validate repository settings from the repo** → Branch protection and package visibility are applied in GitHub by an admin; the committed script and docs make the intended state explicit and re-appliable, and the workflows self-validate the parts they own (pins, permissions, concurrency, provenance) on the next run.

## Migration Plan

1. Resolve the commit SHA for each of the 13 actions' current tags; rewrite all `uses:` in the five workflows to `@<sha> # <tag>`. Push and confirm every workflow still runs green.
2. Add `.github/dependabot.yml` with the `github-actions` ecosystem entry; confirm Dependabot is enabled and enumerates the workflows.
3. Add the `concurrency` block and confirm least-privilege `permissions` in each workflow; enable `provenance: true`/`sbom: true` on the image build and confirm the matrix still publishes.
4. Create the `dockerconfigjson` pull-secret manifest for `ghcr.io` and wire `imagePullSecrets` via the `energyhub` ServiceAccount / Deployments; document the public-package alternative.
5. Author the branch-protection `gh api` script + documentation for `master` and `main` (no direct push, ≥1 review, required `build`/`test` checks); have an admin apply it.
6. Verify end to end: a PR to `master` is blocked without review/passing checks; a real cluster (or a private-image `kind` run without pre-login) pulls the images via the secret.
7. Rollback of the change itself: pins/concurrency/permissions/provenance are additive edits reversible by reverting the workflow commits; the pull secret and Dependabot config are deletable; branch protection is removable via the same `gh api` surface — none affect the running cluster's workloads.

## Open Questions

- Should the GHCR packages ultimately be published **public** (dropping the pull secret entirely) or stay **private** with the pull secret as the standing default for all environments?
- Should the pull secret be materialized at deploy time from the workflow `GITHUB_TOKEN` (short-lived, per-run) or provisioned once from a longer-lived `read:packages` PAT stored as a cluster secret?
- Should a later iteration add keyless signing (cosign/Sigstore) and verify attestations at admission (e.g. via a policy controller), building on the provenance/SBOM introduced here?
- Should required status checks also include the `docker`/image-build workflow, or stay limited to `build` and `test` to avoid gating merges on registry availability?
