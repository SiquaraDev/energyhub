## Why

This change was written when the Fase 17 pipeline had been validated only *locally* (actionlint,
local pytest, adversarial read) and had **never executed on GitHub-hosted runners**. That premise no
longer holds. Applying the four post-1.0.0 hardening changes (`harden-security-credentials`,
`fix-microservices-gaps`, `harden-cicd-supply-chain`, `k8s-production-robustness`) each required a
real push to `master`, so the pipeline has now run **green end-to-end on hosted runners across
multiple commits** — `Build`, `Test`, `Docker`, and the combined `CI/CD Pipeline` all passing, the
five images published to GHCR (`latest` + commit-SHA, now with provenance/SBOM), and the ephemeral
kind `deploy` stage passing image-load → server-side dry-run → core-stack readiness → **rollback
drill**. Three of this change's five original capabilities were therefore proven as a side effect of
shipping the others.

What remains is **not** re-running a 40-step validation of things already green. Two real gaps
survive, and this reduced re-proposal scopes to exactly them:

1. **The proof is ephemeral.** GitHub Actions logs and run history expire; a green run in memory is
   not an auditable record. The milestone-1.0.0 claim of "continuously delivered" needs a durable,
   dated statement that cites the actual runs and catalogs the first-run breakages that were found
   and fixed live.
2. **The optional-secret posture is undecided in writing.** The pipeline runs green with only the
   ambient `GITHUB_TOKEN`; `CODECOV_TOKEN` / `KUBE_CONFIG` / `SLACK_WEBHOOK_URL` are optional. Their
   graceful-degradation behavior has been observed but never recorded as the standing decision.

## What Changes

- Write a **dated pipeline-validation record** (a doc under `docs/`, e.g. `docs/pipeline-validation.md`,
  and/or a dated note in `docs/ci-cd.md`) that: names the validated commit SHA(s); links the green
  `Build`/`Test`/`Docker`/`CI/CD Pipeline` runs; confirms the five GHCR packages carry `latest` +
  SHA (+ provenance/SBOM); quotes the rollback-drill recovery from the kind `deploy` log; and
  **catalogs the first-run breakages that were found and fixed live** during the prior pushes
  (cert-manager CRDs excluded from the non-recursive apply; a GitHub 500 incident that masqueraded as
  a Docker failure; a backtick-in-heredoc that executed as a command; a `jq`-in-`--show` false
  negative; the invalid Kafka KRaft `CLUSTER_ID`).
- **Record the optional-secret posture** as the standing decision: the pipeline SHALL stay green with
  only `GITHUB_TOKEN`; document what each optional secret enables and how to add it, and that the
  gate/soft-fail/no-op degradations are the intended out-of-the-box behavior.
- Make **no** change to workflow behavior — the workflows are the (already-proven) artifact under
  test; this change adds only durable documentation.

## Capabilities

### New Capabilities

- `pipeline-validation-record`: A durable, dated record that the live pipeline was proven green
  end-to-end — Build/Test/Docker/CI-CD runs, GHCR publication with `latest`+SHA, and the kind
  deploy+rollback drill — with the validated commit SHA(s), run references, and a catalog of the
  first-run breakages that were found and fixed live, so the "continuously delivered" claim is
  auditable after Actions log retention expires.
- `repository-secret-configuration`: A recorded standing decision that the pipeline runs green with
  only the ambient `GITHUB_TOKEN`, documenting the graceful-degradation behavior of each optional
  secret (`CODECOV_TOKEN` soft-fails the coverage upload, `KUBE_CONFIG` cleanly skips the real-cluster
  deploy, `SLACK_WEBHOOK_URL` no-ops the notification) and how to enable each, with no secret material
  ever committed.

### Modified Capabilities

None — this change records that the Fase 17 pipeline was proven live; it does not alter what the
workflows do. The Fase 17 specs (`build-automation-workflow`, `test-automation-workflow`,
`docker-image-build`, `container-registry-publishing`, `kubernetes-deploy-automation`,
`deployment-rollback-and-notifications`, `cicd-pipeline-orchestration`) and the post-1.0.0 hardening
capabilities remain the source of truth for behavior.

## Impact

- **Superseded by facts**: The three original capabilities `live-pipeline-execution`,
  `ghcr-publication-verification`, and `ephemeral-deploy-drill-validation` were proven by the real
  pushes of the prior post-1.0.0 changes and are **dropped from this change** — their proof is folded
  into `pipeline-validation-record`. The original 40-task plan (trigger, watch, remediate, verify each
  workflow) is retired; re-running it would re-prove what is already green.
- **Resolved open questions** (settled by later changes, not open anymore): package visibility →
  **private + `ghcr-pull-secret`** is the standing default (`harden-cicd-supply-chain`); requiring
  `Build`/`Test` as merge checks → **branch protection is applied** on `master`
  (`harden-cicd-supply-chain`).
- **Dependencies**: none new. Consumes the already-green Fase 17 workflows and the recorded run
  history.
- **Provides**: an auditable, dated validation record and a documented secret posture — closing the
  last post-1.0.0 gap without touching runtime behavior.
- **Artifacts touched**: a new `docs/` validation record and/or a note in `docs/ci-cd.md`. No
  workflow files, no application code, no manifests.
- **Branch/owner**: default branch `master`; GHCR owner/namespace `siquaradev`.
