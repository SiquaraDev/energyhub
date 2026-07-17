# pipeline-validation-record Specification

## Purpose
TBD - created by archiving change validate-pipeline-live. Update Purpose after archive.
## Requirements
### Requirement: The live-green pipeline is recorded

The change SHALL record that the Fase 17 pipeline was proven green end-to-end on GitHub-hosted
runners — subsuming the three originally-separate proofs. The record MUST attest that, for a named
commit SHA: the `Build`, `Test`, `Docker`, and combined `CI/CD Pipeline` workflows all concluded
green; the five service images published to `ghcr.io/siquaradev/energyhub-<service>` with both
`latest` and the commit-SHA tag; and the ephemeral-kind `deploy` stage passed image-load, server-side
manifest dry-run, core-stack readiness, and the injected-failure rollback drill.

#### Scenario: Record attests the workflows ran green

- **WHEN** the validation record is read
- **THEN** it states that `Build`, `Test`, `Docker`, and `CI/CD Pipeline` concluded green on hosted
  runners for the identified commit SHA, with a reference to each run

#### Scenario: Record attests GHCR publication

- **WHEN** the validation record is read
- **THEN** it shows the five `energyhub-<service>` packages published with `latest` and the commit-SHA
  tag (and the provenance/SBOM attestation on the SHA tag)

#### Scenario: Record attests the deploy and rollback drill

- **WHEN** the validation record is read
- **THEN** it quotes the kind `deploy` stage passing core-stack readiness and the rollback drill
  (rollout fails on a bad image → `rollout undo` → recovery)

### Requirement: First-run breakages are cataloged

The record SHALL catalog the breakages that surfaced only on real runners during the live pushes and
were fixed forward, each with its cause and the fix, so the fix-forward history is auditable rather
than lost with the run logs.

#### Scenario: Each live-found breakage is listed with cause and fix

- **WHEN** the catalog section of the record is read
- **THEN** it lists each first-run-only breakage that occurred (e.g. cert-manager CRDs excluded from
  the non-recursive apply, a GitHub incident misread as a Docker failure, a backtick-in-heredoc
  executed as a command, a `jq`-in-`--show` false negative, an invalid Kafka KRaft `CLUSTER_ID`) with
  its cause and the minimal fix applied

#### Scenario: The record does not weaken acceptance to match a red run

- **WHEN** a cataloged breakage is described
- **THEN** the recorded resolution is a genuine fix that produced a green run, not a relaxation of any
  validation criterion

### Requirement: The record is durable and dated

The change SHALL record the verified-live result durably — a dated document (e.g.
`docs/pipeline-validation.md`) and/or a dated note in `docs/ci-cd.md` — scoped to the validated commit
SHA(s), so the claim is auditable after Actions log retention expires. The record SHALL state it is a
point-in-time attestation and that ongoing green is enforced by the applied branch protection.

#### Scenario: A dated, SHA-scoped record exists

- **WHEN** validation is complete
- **THEN** a dated record states that the pipeline ran green live, references the evidence, identifies
  the validated commit SHA(s), and notes it is a point-in-time attestation backed going forward by the
  required `Build`/`Test` checks

### Requirement: The record contains no secret material

The validation record SHALL NOT contain any credential or secret value; it references runs, SHAs, and
tags only.

#### Scenario: No secret material in the record

- **WHEN** the validation record and any accompanying files are inspected
- **THEN** no plaintext credential, token, or secret value appears in them

