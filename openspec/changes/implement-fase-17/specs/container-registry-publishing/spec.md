## ADDED Requirements

### Requirement: Authenticated registry login

The Docker workflow SHALL authenticate to the target container registry using credentials stored as GitHub secrets, and SHALL NOT embed registry credentials in the workflow file.

#### Scenario: Login uses secrets

- **WHEN** the publish step runs
- **THEN** the workflow logs in to the registry using secret-provided credentials (e.g. `DOCKER_USERNAME`/`DOCKER_PASSWORD`, or ECR login with `ECR_REGISTRY`/`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) and no plaintext credentials appear in the workflow

### Requirement: Images pushed with immutable and rolling tags

Each built image SHALL be pushed to the registry with two tags: a rolling `latest` tag and an immutable tag equal to the commit SHA (`${{ github.sha }}`).

#### Scenario: Image tagged with latest and commit SHA

- **WHEN** a service image is published
- **THEN** it is pushed as both `<registry>/energyhub/<service>:latest` and `<registry>/energyhub/<service>:<sha>`

#### Scenario: SHA tag is immutable and traceable

- **WHEN** a deployed image needs to be traced back to source
- **THEN** the commit-SHA tag identifies the exact commit that produced the image

### Requirement: Configurable registry target

The publishing configuration SHALL support targeting either Docker Hub or AWS ECR, selected through secrets/configuration rather than code changes to the build step.

#### Scenario: Registry target changes via configuration

- **WHEN** the deployment target registry is switched (Docker Hub to ECR or vice versa)
- **THEN** only the login step and registry secrets change, while the build/tag/push structure remains the same
