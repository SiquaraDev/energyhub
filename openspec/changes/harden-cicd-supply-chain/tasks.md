## 1. Pin Actions to Commit SHAs

- [ ] 1.1 Enumerate every `uses:` reference across `build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, and `ci-cd.yml` and list the 13 distinct actions with their current tags
- [ ] 1.2 Resolve the full 40-character commit SHA that each current release tag points to
- [ ] 1.3 Rewrite each `uses: <action>@<tag>` to `uses: <action>@<sha> # <tag>` across all five workflows, preserving the version in the trailing comment
- [ ] 1.4 Confirm no `uses:` reference remains on a mutable tag or branch in any workflow
- [ ] 1.5 Push and confirm all five workflows still run green with the SHA pins

## 2. Automated Pin Updates

- [ ] 2.1 Add `.github/dependabot.yml` with a `package-ecosystem: "github-actions"` entry covering the workflow directory
- [ ] 2.2 Set a review schedule (e.g. weekly) and confirm Dependabot is enabled for the repository
- [ ] 2.3 Confirm Dependabot enumerates the workflows and can open a SHA-bump pull request

## 3. Branch Protection

- [ ] 3.1 Align workflow job/check names so `build.yml` and `test.yml` expose stable, referenceable status-check names
- [ ] 3.2 Author a reproducible `gh api` script (and documentation) that configures branch protection for `master` and `main`
- [ ] 3.3 Encode the rules: block direct pushes, require at least one approving review, and require the build and test status checks
- [ ] 3.4 Have a repository admin apply the script to both default branches
- [ ] 3.5 Verify a direct push is rejected and a PR without review / with failing checks cannot be merged

## 4. Cluster Image-Pull Authentication

- [ ] 4.1 Create a `kubernetes.io/dockerconfigjson` pull-secret manifest for `ghcr.io` in the `energyhub` namespace, sourced from a secret-provided GHCR token (no plaintext)
- [ ] 4.2 Wire `imagePullSecrets` into the service pods via the namespace ServiceAccount and/or each service Deployment (auth, client, contract, financial, audit)
- [ ] 4.3 Document the public-package alternative (making GHCR packages public) and its trade-off
- [ ] 4.4 Verify a private `ghcr.io/siquaradev/energyhub-<service>-service` image is pulled successfully instead of `ImagePullBackOff`

## 5. Workflow Supply-Chain Hardening

- [ ] 5.1 Confirm each workflow declares a least-privilege default `permissions: contents: read`
- [ ] 5.2 Confirm `packages: write` is granted only to the publish job and `packages: read` only to the deploy job
- [ ] 5.3 Add a `concurrency` group keyed by `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true` to each workflow
- [ ] 5.4 Enable `provenance: true` and `sbom: true` on `docker/build-push-action` in `docker.yml` and `ci-cd.yml`
- [ ] 5.5 Confirm the image matrix still builds/publishes green and that a superseded run is cancelled by a newer push

## 6. Validation

- [ ] 6.1 Confirm all workflows pass with SHA pins, least-privilege permissions, concurrency guards, and provenance/SBOM enabled
- [ ] 6.2 Confirm published images carry a provenance attestation and SBOM
- [ ] 6.3 Confirm branch protection blocks unreviewed/failing merges on `master` and `main`
- [ ] 6.4 Confirm the cluster pulls private GHCR images via the pull secret
- [ ] 6.5 Run `openspec validate harden-cicd-supply-chain --strict` and confirm the change is valid
