## 1. CI Foundation and Secrets

- [ ] 1.1 Create the `.github/workflows/` directory in the repository root
- [ ] 1.2 Configure the registry secrets in GitHub (`DOCKER_USERNAME`/`DOCKER_PASSWORD`, or `ECR_REGISTRY`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`)
- [ ] 1.3 Configure the `KUBE_CONFIG` secret (`kubectl config view --raw`) and any Slack webhook secret used for notifications

## 2. Build Automation Workflow

- [ ] 2.1 Create `.github/workflows/build.yml` triggered on `push` to `main`/`develop` and `pull_request` to `main`
- [ ] 2.2 Add steps to check out code, set up Python 3.12, install Poetry, and run `poetry install --no-interaction`
- [ ] 2.3 Add `poetry build` and `poetry run pytest` steps so the job fails on build or test failure
- [ ] 2.4 Add coverage generation (`--cov=energyhub --cov-report=xml`) and upload the report to the coverage service
- [ ] 2.5 Commit, push, and confirm the build workflow runs green in GitHub Actions

## 3. Test Automation Workflow

- [ ] 3.1 Create `.github/workflows/test.yml` triggered on `push` to `main`/`develop`/`feature/*` and `pull_request` to `main`/`develop`
- [ ] 3.2 Define Postgres and Redis `services` with health checks and exposed ports
- [ ] 3.3 Add the environment setup steps (checkout, Python 3.12, Poetry, dependency install)
- [ ] 3.4 Add a separate unit test step (`pytest tests/unit`) and an integration step (`pytest tests/integration`) with `DATABASE_URL`/`REDIS_URL` pointing at the services
- [ ] 3.5 Add an `if: always()` step that uploads test/coverage results as an artifact
- [ ] 3.6 Commit, push, and confirm unit and integration tests run against the service containers

## 4. Docker Image Build

- [ ] 4.1 Create `.github/workflows/docker.yml` triggered on `push` to `main`/`develop` and `pull_request` to `main`
- [ ] 4.2 Define a build matrix over `auth-service`, `client-service`, `contract-service`, `financial-service`, `audit-service`, `api-gateway`
- [ ] 4.3 Add the Buildx setup step and a `docker/build-push-action` build using `./services/<service>` as context
- [ ] 4.4 Configure registry-backed layer caching via `cache-from`/`cache-to`
- [ ] 4.5 Commit, push, and confirm all service images build in the matrix

## 5. Container Registry Publishing

- [ ] 5.1 Add the registry login step (Docker Hub or AWS ECR) using the configured secrets, with no plaintext credentials in the workflow
- [ ] 5.2 Set `push: true` and tag each image as both `:latest` and `:${{ github.sha }}`
- [ ] 5.3 Document the ECR alternative (login + tags) so the registry target can be switched via configuration
- [ ] 5.4 Trigger the workflow and confirm images appear in the registry with both tags

## 6. Kubernetes Deploy Automation

- [ ] 6.1 Create `.github/workflows/deploy.yml` triggered on `push` to `main`
- [ ] 6.2 Add the step that configures `kubectl` context from the `KUBE_CONFIG` secret
- [ ] 6.3 Add the step applying the `k8s/` manifests (namespace, configmap, secret, and workloads)
- [ ] 6.4 Add `kubectl rollout status` verification for `auth-service`, `client-service`, and `api-gateway`
- [ ] 6.5 Commit, push to `main`, and confirm the deploy runs and rollout status is verified

## 7. Deployment Rollback and Notifications

- [ ] 7.1 Add a readiness gate using `kubectl wait --for=condition=available --timeout=300s` for the key Deployments
- [ ] 7.2 Add an `if: failure()` step running `kubectl rollout undo` for the affected Deployments
- [ ] 7.3 Add an `if: failure()` Slack notification step reporting the job status
- [ ] 7.4 Test rollback by deploying an intentionally broken revision and confirming automatic rollback and notification

## 8. CI/CD Pipeline Orchestration

- [ ] 8.1 Create the combined `.github/workflows/ci-cd.yml` with `build-and-test`, `build-and-push`, and `deploy` jobs
- [ ] 8.2 Wire ordering with `needs` so `build-and-push` follows `build-and-test` and `deploy` follows `build-and-push`
- [ ] 8.3 Push to `main` and confirm the staged pipeline runs end to end with correct ordering
- [ ] 8.4 Document the pipeline, required secrets, and deploy/rollback flow in `docs/ci-cd.md`

## 9. Validation

- [ ] 9.1 Confirm build, test, Docker, publish, and deploy workflows each run successfully
- [ ] 9.2 Confirm images are published with `latest` and commit-SHA tags
- [ ] 9.3 Confirm the full pipeline deploys to Kubernetes and that rollback triggers on an injected failure
- [ ] 9.4 Run `openspec validate implement-fase-17` and confirm the change is valid
