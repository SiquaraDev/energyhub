## Why

Fase 15 containerized the services and Fase 16 authored the Kubernetes manifests, but every build, test, image push, and deploy is still run by hand — slow, error-prone, and impossible to gate on a green test suite. This phase, the final one in the roadmap, adds GitHub Actions pipelines so that on every push the code is built, tested, imaged, published, and deployed automatically, with rollback on failure — turning the platform into a production-ready, continuously delivered backend.

## What Changes

- Add a build workflow `.github/workflows/build.yml` that, on push/PR to the main branches, checks out the code, sets up Python 3.12 with Poetry, installs dependencies, runs `poetry build`, executes the test suite, and uploads a coverage report.
- Add a test workflow `.github/workflows/test.yml` that provisions Postgres and Redis service containers (with health checks), runs the unit and integration suites against them via `DATABASE_URL`/`REDIS_URL`, and uploads test/coverage artifacts even on failure.
- Add a Docker workflow `.github/workflows/docker.yml` that builds an image per service using a build matrix and Buildx, with registry-backed layer caching (`cache-from`/`cache-to`).
- Publish the built images to a container registry (Docker Hub or AWS ECR), authenticated via GitHub secrets, tagging each image with both `latest` and the commit SHA for traceable, immutable releases.
- Add a deploy workflow `.github/workflows/deploy.yml` that, on push to `main`, configures `kubectl` from a `KUBE_CONFIG` secret, applies the `k8s/` manifests, and verifies each Deployment's rollout status.
- Add automatic rollback: gate readiness with `kubectl wait`, run `kubectl rollout undo` on failure, and send a failure notification to Slack.
- Add an end-to-end `CI/CD Pipeline` workflow that chains build-and-test → build-and-push → deploy via job `needs` dependencies, and document the pipeline in `docs/ci-cd.md`.

## Capabilities

### New Capabilities

- `build-automation-workflow`: A GitHub Actions workflow that installs Poetry, builds the package, runs tests, and reports coverage on every push/PR to the protected branches.
- `test-automation-workflow`: A test workflow that spins up Postgres/Redis service containers with health checks and runs the unit and integration suites against them, publishing results as artifacts.
- `docker-image-build`: A matrix workflow that builds one Docker image per service via Buildx with registry layer caching.
- `container-registry-publishing`: Secret-authenticated push of the built images to a container registry, tagged with `latest` and the commit SHA.
- `kubernetes-deploy-automation`: A deploy workflow that configures `kubectl` from a secret, applies the `k8s/` manifests on `main`, and verifies rollout status.
- `deployment-rollback-and-notifications`: Readiness gating, automatic `rollout undo` on failure, and failure notifications so a bad release self-heals and alerts the team.
- `cicd-pipeline-orchestration`: An end-to-end pipeline that chains build/test, image publish, and deploy through job dependencies, documented in `docs/ci-cd.md`.

### Modified Capabilities

None — this phase introduces the CI/CD automation; no previously specified requirements change.

## Impact

- **Dependencies**: GitHub Actions and community actions (`actions/checkout@v4`, `actions/setup-python@v5`, `snok/install-poetry@v1`, `docker/setup-buildx-action@v3`, `docker/login-action@v3`, `docker/build-push-action@v5`, `azure/k8s-set-context@v4`, `codecov/codecov-action`, `8398a7/action-slack@v3`). No changes to application runtime dependencies.
- **Consumes**: The per-service `Dockerfile`s from Fase 15, the `k8s/` manifests from Fase 16, the Poetry project from Fase 1, and the test suites from Fase 13.
- **Provides**: Automated build, test, image publishing, deploy, and rollback pipelines runnable on every push, plus pipeline documentation.
- **New artifacts**: `.github/workflows/` (`build.yml`, `test.yml`, `docker.yml`, `deploy.yml`, and the combined `ci-cd.yml`) and `docs/ci-cd.md`.
- **Secrets/coordination**: Requires repository secrets to be configured — `DOCKER_USERNAME`/`DOCKER_PASSWORD` (or `ECR_REGISTRY`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) and `KUBE_CONFIG`; the deploy target is the Fase 16 cluster and the manifests there remain the source of truth for desired state.
