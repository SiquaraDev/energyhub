## Context

The original design assumed the Fase 17 pipeline had "never executed on GitHub-hosted runners." That
assumption was overtaken by events: to ship the four post-1.0.0 hardening changes, the pipeline was
pushed to `master` repeatedly and now has a track record of green end-to-end runs on hosted runners.
Concretely, as of the `k8s-production-robustness` push (`434a094`) and several before it:

- `Build`, `Test`, `Docker`, and `CI/CD Pipeline` all conclude **green** on `ubuntu-latest`.
- The five images publish to `ghcr.io/siquaradev/energyhub-<service>` with `latest` + the commit SHA,
  and (since `harden-cicd-supply-chain`) carry provenance + SBOM attestations.
- The `ci-cd.yml` `deploy` job genuinely runs on an ephemeral kind cluster: image load → server-side
  dry-run → core-stack readiness → the injected-failure **rollback drill** → recovery — and (since
  `k8s-production-robustness`) applies the Kustomize `dev` overlay with PVC-backed backends.

So `live-pipeline-execution`, `ghcr-publication-verification`, and `ephemeral-deploy-drill-validation`
are already true. This reduced change does not re-prove them; it **captures** them and closes the two
things that shipping the others did *not* incidentally produce: a durable record and a written secret
posture. The workflows remain the artifact; this change adds only documentation.

## Goals / Non-Goals

**Goals:**
- Produce a durable, dated validation record that cites the actual green runs (commit SHA, workflow
  run references), confirms GHCR publication (`latest`+SHA+attestations), and quotes the rollback-drill
  recovery — surviving Actions log-retention expiry.
- Catalog, in that record, the first-run breakages that were found and fixed live during the prior
  pushes, so the fix-forward history is auditable.
- Record the optional-secret posture as the standing decision (green with only `GITHUB_TOKEN`; the
  per-secret degradation is intended), with instructions to enable each.

**Non-Goals:**
- No workflow behavior changes — the pipeline is the proven artifact, not the thing being edited.
- No re-triggering a 40-step validation of already-green stages.
- No standing real cluster; the ephemeral-kind proof remains the acceptance path for deploy+rollback,
  and `deploy.yml` stays cleanly gated behind `KUBE_CONFIG`.
- No new secret-management platform; secrets stay as GitHub repository secrets.
- No branch-protection authoring here — it was already applied in `harden-cicd-supply-chain`.

## Decisions

**Fold the three proven capabilities into the validation record instead of re-specifying them:**
- **Decision:** Drop the `live-pipeline-execution`, `ghcr-publication-verification`, and
  `ephemeral-deploy-drill-validation` capabilities; let `pipeline-validation-record` encode their
  proof (runs green, images published, deploy+rollback drill passed) as recorded evidence.
- **Rationale:** They were point-in-time validations, not ongoing invariants — the ongoing behavior is
  already specified by the Fase 17 capabilities. Recording the proof once, with links, is the durable
  artifact; three parallel "was proven" specs would be redundant.
- **Alternative considered:** Keep all five and mark three "already satisfied" — rejected as ceremony
  that inflates the spec surface without adding an enforceable requirement.

**The record is a committed doc, not reliance on Actions history:**
- **Decision:** Write `docs/pipeline-validation.md` (and/or a dated note in `docs/ci-cd.md`) with the
  commit SHA(s), run references, GHCR listing, and the rollback-drill excerpt.
- **Rationale:** Actions logs and run retention expire; a committed, dated doc is the auditable
  long-term proof. This answers the original design's open question about where the evidence should live.
- **Alternative considered:** Rely on the Actions run list alone — rejected as non-durable.

**Graceful degradation is the recorded standing posture, not a to-do:**
- **Decision:** Record that the pipeline runs green with only `GITHUB_TOKEN`; document each optional
  secret's effect and how to add it, and that the gate-skip / soft-fail / no-op behaviors are
  intended. Do not require any optional secret for "green."
- **Rationale:** The behavior is already observed across the prior runs (Deploy gate skips cleanly
  without `KUBE_CONFIG`, etc.); the remaining work is to write it down as the decision, not to test it.
- **Alternative considered:** Make secrets mandatory — rejected; it contradicts the out-of-the-box
  design and would couple the milestone to external accounts.

## Risks / Trade-offs

- **A recorded run reference rots** (repo renamed, logs expire) → The record cites the immutable commit
  SHA and the durable facts (image tags, the fixed breakages) that remain verifiable from the repo and
  GHCR even after Actions logs expire; the run URL is a convenience, not the sole proof.
- **The record drifts from reality** (a later change breaks the pipeline) → The record is dated and
  scoped to specific commit SHA(s); it is a point-in-time attestation, not a claim of perpetual green.
  Ongoing green is enforced by the (applied) branch protection requiring `Build`/`Test`.
- **Catalog of fixes is incomplete** → The prior changes' `tasks.md`/`design.md` amendments already
  record each fix; the record consolidates and cross-links them rather than reconstructing from memory.

## Migration Plan

1. Assemble the evidence from the already-green runs: the validated commit SHA(s); the `Build`/`Test`/
   `Docker`/`CI/CD Pipeline` run references; the GHCR package/tag listing; the rollback-drill recovery
   log excerpt.
2. Write `docs/pipeline-validation.md` (and/or a dated note in `docs/ci-cd.md`) containing that
   evidence and the catalog of first-run breakages found-and-fixed live.
3. Document the optional-secret posture (green with only `GITHUB_TOKEN`; per-secret effect + how to
   enable) in the same record or `docs/ci-cd.md`.
4. Validate the record: every cited SHA/tag is real, no secret material is committed, and the
   degradation claims match the observed run behavior.
5. Rollback of *this* change: it adds only documentation; deleting the record returns to the prior
   state with no effect on any workflow or cluster.

## Open Questions

- ~~Public vs private GHCR packages?~~ **RESOLVED (harden-cicd-supply-chain)** — private is the
  standing default, pulled via the `ghcr-pull-secret`.
- ~~Require `Build`/`Test` as merge checks?~~ **RESOLVED (harden-cicd-supply-chain)** — branch
  protection is applied on `master` requiring both.
- ~~Where should the durable evidence live?~~ **RESOLVED here** — a committed `docs/` validation
  record (Actions history is non-durable).
- **STILL OPEN** — Should the real-cluster `deploy.yml` path (behind `KUBE_CONFIG`) be proven for the
  milestone, or is the ephemeral-kind proof sufficient? This change treats ephemeral-kind as
  sufficient and the real path as optional; standing up a cluster remains out of scope.
