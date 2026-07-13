## 1. Pre-flight and secret posture

- [ ] 1.1 Confirm the five workflows (`build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, `ci-cd.yml`) and `docs/ci-cd.md` are present on `master` and `actionlint` is still clean locally
- [ ] 1.2 Decide the secret posture: either configure optional secrets (task group 2) or validate the out-of-the-box secretless path
- [ ] 1.3 Confirm the GHCR owner resolves to `siquaradev` (lowercased `SiquaraDev`) and note the target refs `ghcr.io/siquaradev/energyhub-<service>`

## 2. Repository secret configuration (user-driven, optional)

- [ ] 2.1 (Optional) Add `CODECOV_TOKEN` as a repository secret, or record that the coverage upload soft-fails without it (`fail_ci_if_error: false`)
- [ ] 2.2 (Optional) Add `KUBE_CONFIG` as a repository secret for the real-cluster `deploy.yml` path, or record that the deploy gate skips cleanly without it
- [ ] 2.3 (Optional) Add `SLACK_WEBHOOK_URL` as a repository secret, or record that the failure-notification step no-ops without it
- [ ] 2.4 Confirm no secret material appears in any committed file or workflow log

## 3. Trigger the first live run (user-driven)

- [ ] 3.1 Push a commit to `master` to trigger `Build`, `Test`, `Docker`, and `CI/CD Pipeline` on GitHub-hosted runners
- [ ] 3.2 Record the resolved commit SHA and the four workflow run URLs

## 4. Validate the Build workflow

- [ ] 4.1 Confirm the `Build` run installs Python 3.12 + Poetry, runs `poetry build`, and concludes green
- [ ] 4.2 Confirm `pytest --cov` meets the embedded 80% coverage gate
- [ ] 4.3 Confirm the Codecov upload behaves per the chosen secret posture (uploads with token, or soft-fails without failing the job)

## 5. Validate the Test workflow

- [ ] 5.1 Confirm Postgres 16 and Redis 7 service containers start and pass their health checks
- [ ] 5.2 Confirm `alembic upgrade head` applies the schema before the integration step
- [ ] 5.3 Confirm the integration step runs against the service containers (integration tests execute, not skipped) and the job concludes green
- [ ] 5.4 Confirm the `if: always()` step uploads the test/coverage artifact

## 6. Validate the Docker workflow and GHCR publication

- [ ] 6.1 Confirm the matrix builds all five service images (`auth`, `client`, `contract`, `financial`, `audit`) via Buildx
- [ ] 6.2 Confirm login to `ghcr.io` uses `github.actor` + `GITHUB_TOKEN` with `packages: write` and requires no external registry secret
- [ ] 6.3 Confirm the five `energyhub-<service>` packages appear under the `siquaradev` owner in GHCR
- [ ] 6.4 Confirm each image carries both the `latest` tag and the commit-SHA tag, and record the package/tag listing

## 7. Validate the ephemeral-kind deploy stage (ci-cd.yml)

- [ ] 7.1 Confirm the combined pipeline runs `build-and-test` → `build-and-push` → `deploy` in order via `needs`
- [ ] 7.2 Confirm the `deploy` job creates the `energyhub` kind cluster and frees disk space as needed
- [ ] 7.3 Confirm each SHA-tagged image is pulled, retagged to `energyhub-<svc>-service:latest`, and loaded into kind
- [ ] 7.4 Confirm the server-side dry-run passes for every `k8s/` manifest, then the real apply succeeds
- [ ] 7.5 Confirm services are scaled to 1 replica and the core stack (Postgres/Redis/RabbitMQ/Consul + auth/client) reaches `condition=available` within timeout
- [ ] 7.6 Confirm the rollback drill: bad image → rollout does NOT complete → `rollout undo` → `auth-service` recovers

## 8. Validate graceful degradation

- [ ] 8.1 Confirm the pipeline is green using only the ambient `GITHUB_TOKEN` (no optional secrets), if validating the secretless path
- [ ] 8.2 Confirm the `deploy.yml` gate emits `has_kubeconfig=false` and skips the real deploy cleanly when `KUBE_CONFIG` is absent
- [ ] 8.3 Confirm the Slack step is skipped (guarded by `env.SLACK_WEBHOOK_URL != ''`) and does not fail the workflow when the webhook is absent

## 9. Remediate first-run breakages

- [ ] 9.1 Triage any red run and identify the runner-only root cause (action version drift, casing, disk/RAM, publish race)
- [ ] 9.2 Apply a minimal fix in the affected workflow (do not weaken acceptance criteria) and re-push
- [ ] 9.3 Repeat until `Build`, `Test`, `Docker`, and `CI/CD Pipeline` all conclude green on the same commit

## 10. (Optional) Prove the real-cluster deploy path

- [ ] 10.1 If a real cluster is available, make the GHCR packages public or configure an `imagePullSecret` so the cluster can pull the SHA-tagged images
- [ ] 10.2 With `KUBE_CONFIG` set, push to `master` and confirm `deploy.yml` applies `k8s/`, pins images to the SHA, verifies rollout, and (on injected failure) rolls back and notifies

## 11. Record the verified pipeline

- [ ] 11.1 Assemble the evidence set: run URLs, validated commit SHA, GHCR package/tag listing, rollback-drill recovery log excerpt
- [ ] 11.2 Add a dated "verified live" note to `docs/ci-cd.md` and/or a validation record referencing the evidence and the commit SHA
- [ ] 11.3 Note any follow-ups surfaced by the live run (e.g. branch protection requiring `Build`/`Test`, GHCR visibility decision)

## 12. Validation

- [ ] 12.1 Confirm all four workflows concluded green on the validated commit and the images are published with both tags
- [ ] 12.2 Confirm the ephemeral-kind deploy and rollback drill passed end to end
- [ ] 12.3 Run `openspec validate validate-pipeline-live --strict` and confirm the change is valid
