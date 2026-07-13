## Why

Fase 17 delivered a working GitHub Actions pipeline (build, test, image publish, deploy, rollback), but its supply chain is soft: every action is pinned to a mutable tag (`@v7`, `@v1`) that a compromised upstream can silently repoint at malicious code, the default branch `master` has no required checks or review so unverified code can land directly, and the GHCR packages are born private so a real cluster cannot pull them without credentials. This change hardens that surface — immutable pins, enforced branch protection, and authenticated image pulls — so the 1.0.0 pipeline is trustworthy end to end, not just functional.

## What Changes

- Pin every GitHub Actions `uses:` reference across the five workflows in `.github/workflows/` (`build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, `ci-cd.yml`) to a full 40-character commit SHA instead of a moving tag, each with a trailing comment recording the human-readable version (e.g. `uses: actions/checkout@<sha> # v7`). Covers all 13 distinct actions in use (`actions/checkout`, `actions/setup-python`, `snok/install-poetry`, `actions/cache`, `codecov/codecov-action`, `actions/upload-artifact`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/build-push-action`, `azure/k8s-set-context`, `slackapi/slack-github-action`, `helm/kind-action`).
- Add a Dependabot configuration (`.github/dependabot.yml`) for the `github-actions` ecosystem so the SHA pins are kept current through reviewable, automated bump PRs rather than drifting stale.
- Enforce branch protection on `master` (and `main`): disallow direct pushes, require changes to arrive via pull request with at least one approving review, and require the build and test workflows to pass as status checks before merge. Because these are GitHub repository settings that live outside the workflow files, they are documented and captured as a reproducible `gh api` configuration script; the workflows are aligned to expose stable, referenceable check names.
- Make the GHCR images consumable by a real Kubernetes cluster by creating a `kubernetes.io/dockerconfigjson` image-pull secret for `ghcr.io` in the `energyhub` namespace and wiring it into the service workloads (via the namespace ServiceAccount and/or each Deployment's `imagePullSecrets`), so private packages under `ghcr.io/siquaradev/...` can be pulled. Document making the packages public as the simpler alternative.
- Harden each workflow's operational surface: confirm least-privilege `permissions` (default `contents: read`, elevate `packages: write` only where publishing), add `concurrency` guards that cancel superseded runs per ref, and enable build provenance and SBOM attestation (`provenance: true`/`sbom: true`) on the image build so published images carry verifiable origin metadata.

## Capabilities

### New Capabilities

- `github-actions-sha-pinning`: All workflow `uses:` references are pinned to immutable commit SHAs with a version comment, across all five workflows, kept current by Dependabot for the `github-actions` ecosystem.
- `branch-protection-rules`: The default branches are protected — no direct pushes, mandatory PR review, and required passing build/test status checks before merge — captured as reproducible repository settings.
- `cluster-image-pull-authentication`: The cluster can pull the private GHCR images via a `dockerconfigjson` image-pull secret wired into the service workloads, with a documented public-package alternative and credentials sourced only from secrets.
- `workflow-supply-chain-hardening`: Least-privilege workflow permissions, concurrency guards that cancel superseded runs, and build provenance/SBOM attestation on published images.

### Modified Capabilities

None — this change adds new supply-chain hardening behavior on top of the Fase 17 pipeline; it does not alter the previously specified build/test/publish/deploy requirements.

## Impact

- **Dependencies**: No application runtime dependency changes. Introduces a Dependabot config and depends on the exact upstream release commits of the 13 actions already in use. Requires a GHCR-scoped token (the workflow `GITHUB_TOKEN`, or a `read:packages` PAT) to materialize the cluster image-pull secret.
- **Consumes**: The Fase 17 workflows (`.github/workflows/*`) and GHCR publishing, and the Fase 16 Kubernetes Deployments/ServiceAccounts in `k8s/` that must pull the images.
- **Provides**: A tamper-resistant, review-gated, pull-authenticated delivery pipeline — immutable action pins, enforced branch protection, and cluster-pullable images with provenance/SBOM metadata.
- **New artifacts**: `.github/dependabot.yml`, a Kubernetes image-pull secret manifest (and `imagePullSecrets` wiring in `k8s/`), a branch-protection configuration script/doc under `.github/` or `docs/`, and edits to the five existing workflow files (SHA pins, `concurrency`, provenance/SBOM).
- **Repository settings/coordination**: Branch protection and repository package visibility are configured in GitHub settings (outside the workflow files) and must be applied by a repo admin; the `gh api` script and documentation make that reproducible. The GHCR namespace is the lowercased owner `ghcr.io/siquaradev/...` and the default branch is `master`.
