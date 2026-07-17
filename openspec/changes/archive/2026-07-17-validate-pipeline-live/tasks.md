# Tasks — validate-pipeline-live (reduced re-proposal)

> **Scope note.** The original 40-task plan (trigger the first run, watch each of Build/Test/Docker/
> CI-CD, remediate, verify) is **retired**: the pipeline was already proven green live by the pushes
> of the four prior post-1.0.0 changes. The three capabilities `live-pipeline-execution`,
> `ghcr-publication-verification`, and `ephemeral-deploy-drill-validation` are dropped; their proof is
> folded into `pipeline-validation-record`. What remains is to write the durable record and document
> the secret posture.

## 1. Assemble the evidence (already-green runs)

- [x] 1.1 Identify the validated commit SHA(s) whose `Build`, `Test`, `Docker`, and `CI/CD Pipeline`
      runs concluded green (e.g. the `k8s-production-robustness` push and prior), and collect their run
      references
- [x] 1.2 Capture the GHCR listing for the five `energyhub-<service>` packages showing `latest` + the
      commit-SHA tag (and the provenance/SBOM attestation on the SHA tag)
- [x] 1.3 Extract the rollback-drill recovery excerpt from the `ci-cd.yml` `deploy` job log ("rollout
      failed as expected → `rollout undo` → recovered"), and the core-stack `condition met` lines

## 2. Write the dated validation record

- [x] 2.1 Create `docs/pipeline-validation.md` (and/or a dated "verified live" note in `docs/ci-cd.md`)
      recording: the validated commit SHA(s), the run references, the GHCR package/tag listing, and
      the rollback-drill recovery excerpt
- [x] 2.2 In that record, catalog the first-run breakages found and fixed **live** during the prior
      pushes, each with its cause and fix: cert-manager CRDs excluded from the non-recursive apply; a
      GitHub 500 incident that masqueraded as a Docker failure (proven by a zero-change re-run);
      a backtick-in-heredoc that executed as a command; a `jq`-in-`--show` false negative; the invalid
      Kafka KRaft `CLUSTER_ID`
- [x] 2.3 State the record is a **dated, point-in-time attestation** scoped to the cited SHA(s), and
      that ongoing green is enforced by the applied branch protection (Build/Test required)

## 3. Record the optional-secret posture

- [x] 3.1 Document that the pipeline runs green with only the ambient `GITHUB_TOKEN`, and the effect +
      enable-step of each optional secret: `CODECOV_TOKEN` (coverage upload soft-fails,
      `fail_ci_if_error: false`), `KUBE_CONFIG` (gate emits `has_kubeconfig=false`, real deploy
      skipped clean), `SLACK_WEBHOOK_URL` (failure notification no-ops via `env … != ''`)
- [x] 3.2 Confirm no secret material appears in any committed file or the record itself

## 4. Validation

- [x] 4.1 Verify every cited commit SHA and image tag in the record is real (resolvable in the repo /
      GHCR), and the degradation claims match the observed run behavior
- [x] 4.2 Run the plaintext-secrets guard (`scripts/check_no_plaintext_secrets.sh`) and confirm the
      record introduced no credential
- [x] 4.3 Run `openspec validate validate-pipeline-live --strict` and confirm the change is valid
