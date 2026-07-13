## ADDED Requirements

### Requirement: All five service images published to GHCR

The live pipeline run SHALL publish one image per service for `auth-service`, `client-service`, `contract-service`, `financial-service`, and `audit-service` to the GitHub Container Registry under `ghcr.io/siquaradev/energyhub-<service>`, and all five packages SHALL be verifiably present after the run.

#### Scenario: Five packages appear in GHCR

- **WHEN** the `Docker` (and combined `build-and-push`) matrix completes green
- **THEN** GHCR lists the five packages `energyhub-auth-service`, `energyhub-client-service`, `energyhub-contract-service`, `energyhub-financial-service`, and `energyhub-audit-service` under the `siquaradev` owner

#### Scenario: Owner is lowercased in the OCI reference

- **WHEN** an image reference is published
- **THEN** the owner segment is `siquaradev` (the `SiquaraDev` owner lowercased), producing a valid OCI reference

### Requirement: Each image carries both a rolling and an immutable tag

Each published service image SHALL carry two tags: the rolling `latest` tag and an immutable tag equal to the commit SHA (`${{ github.sha }}`) of the validation run.

#### Scenario: Image is tagged latest and commit SHA

- **WHEN** a service image is published
- **THEN** it is available as both `ghcr.io/siquaradev/energyhub-<service>:latest` and `ghcr.io/siquaradev/energyhub-<service>:<sha>`

#### Scenario: SHA tag traces back to the commit

- **WHEN** a published image is inspected by its SHA tag
- **THEN** the tag equals the exact commit SHA of the validation push, tying the image to its source

### Requirement: Publication authenticated by the ambient GITHUB_TOKEN

The publish step SHALL authenticate to GHCR using `github.actor` and the ambient `GITHUB_TOKEN` with `packages: write` permission, requiring no externally configured registry secret.

#### Scenario: Login uses the built-in token

- **WHEN** the publish step logs in to `ghcr.io`
- **THEN** it authenticates with `github.actor` and `secrets.GITHUB_TOKEN` and the push succeeds without any external registry secret
