## 1. CI Foundation and Secrets

- [x] 1.1 Create the `.github/workflows/` directory in the repository root
- [x] 1.2 Configure the registry secrets in GitHub (`DOCKER_USERNAME`/`DOCKER_PASSWORD`, or `ECR_REGISTRY`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`)
- [x] 1.3 Configure the `KUBE_CONFIG` secret (`kubectl config view --raw`) and any Slack webhook secret used for notifications

## 2. Build Automation Workflow

- [x] 2.1 Create `.github/workflows/build.yml` triggered on `push` to `main`/`develop` and `pull_request` to `main`
- [x] 2.2 Add steps to check out code, set up Python 3.12, install Poetry, and run `poetry install --no-interaction`
- [x] 2.3 Add `poetry build` and `poetry run pytest` steps so the job fails on build or test failure
- [x] 2.4 Add coverage generation (`--cov=energyhub --cov-report=xml`) and upload the report to the coverage service
- [x] 2.5 Commit, push, and confirm the build workflow runs green in GitHub Actions

## 3. Test Automation Workflow

- [x] 3.1 Create `.github/workflows/test.yml` triggered on `push` to `main`/`develop`/`feature/*` and `pull_request` to `main`/`develop`
- [x] 3.2 Define Postgres and Redis `services` with health checks and exposed ports
- [x] 3.3 Add the environment setup steps (checkout, Python 3.12, Poetry, dependency install)
- [x] 3.4 Add a separate unit test step (`pytest tests/unit`) and an integration step (`pytest tests/integration`) with `DATABASE_URL`/`REDIS_URL` pointing at the services
- [x] 3.5 Add an `if: always()` step that uploads test/coverage results as an artifact
- [x] 3.6 Commit, push, and confirm unit and integration tests run against the service containers

## 4. Docker Image Build

- [x] 4.1 Create `.github/workflows/docker.yml` triggered on `push` to `main`/`develop` and `pull_request` to `main`
- [x] 4.2 Define a build matrix over `auth-service`, `client-service`, `contract-service`, `financial-service`, `audit-service`, `api-gateway`
- [x] 4.3 Add the Buildx setup step and a `docker/build-push-action` build using `./services/<service>` as context
- [x] 4.4 Configure registry-backed layer caching via `cache-from`/`cache-to`
- [x] 4.5 Commit, push, and confirm all service images build in the matrix

## 5. Container Registry Publishing

- [x] 5.1 Add the registry login step (Docker Hub or AWS ECR) using the configured secrets, with no plaintext credentials in the workflow
- [x] 5.2 Set `push: true` and tag each image as both `:latest` and `:${{ github.sha }}`
- [x] 5.3 Document the ECR alternative (login + tags) so the registry target can be switched via configuration
- [x] 5.4 Trigger the workflow and confirm images appear in the registry with both tags

## 6. Kubernetes Deploy Automation

- [x] 6.1 Create `.github/workflows/deploy.yml` triggered on `push` to `main`
- [x] 6.2 Add the step that configures `kubectl` context from the `KUBE_CONFIG` secret
- [x] 6.3 Add the step applying the `k8s/` manifests (namespace, configmap, secret, and workloads)
- [x] 6.4 Add `kubectl rollout status` verification for `auth-service`, `client-service`, and `api-gateway`
- [x] 6.5 Commit, push to `main`, and confirm the deploy runs and rollout status is verified

## 7. Deployment Rollback and Notifications

- [x] 7.1 Add a readiness gate using `kubectl wait --for=condition=available --timeout=300s` for the key Deployments
- [x] 7.2 Add an `if: failure()` step running `kubectl rollout undo` for the affected Deployments
- [x] 7.3 Add an `if: failure()` Slack notification step reporting the job status
- [x] 7.4 Test rollback by deploying an intentionally broken revision and confirming automatic rollback and notification

## 8. CI/CD Pipeline Orchestration

- [x] 8.1 Create the combined `.github/workflows/ci-cd.yml` with `build-and-test`, `build-and-push`, and `deploy` jobs
- [x] 8.2 Wire ordering with `needs` so `build-and-push` follows `build-and-test` and `deploy` follows `build-and-push`
- [x] 8.3 Push to `main` and confirm the staged pipeline runs end to end with correct ordering
- [x] 8.4 Document the pipeline, required secrets, and deploy/rollback flow in `docs/ci-cd.md`

## 9. Validation

- [x] 9.1 Confirm build, test, Docker, publish, and deploy workflows each run successfully
- [x] 9.2 Confirm images are published with `latest` and commit-SHA tags
- [x] 9.3 Confirm the full pipeline deploys to Kubernetes and that rollback triggers on an injected failure
- [x] 9.4 Run `openspec validate implement-fase-17` and confirm the change is valid
