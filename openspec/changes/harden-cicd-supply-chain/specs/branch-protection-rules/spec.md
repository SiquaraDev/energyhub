## ADDED Requirements

### Requirement: Protected default branches

The repository SHALL protect the default branch `master` and the `main` branch so that commits cannot be pushed directly to them and all changes arrive through a pull request.

#### Scenario: Direct push is rejected

- **WHEN** a contributor attempts to push a commit directly to `master` or `main`
- **THEN** the push is rejected by branch protection and the change must be submitted as a pull request

#### Scenario: Both default branches are covered

- **WHEN** the branch-protection configuration is enumerated
- **THEN** protection rules exist for both `master` and `main`

### Requirement: Required pull-request review

Merging into a protected branch SHALL require at least one approving pull-request review, so that no change lands without a second set of eyes.

#### Scenario: Merge blocked without approval

- **WHEN** a pull request targeting `master` has no approving review
- **THEN** the merge is blocked until at least one approving review is recorded

### Requirement: Required passing status checks before merge

Merging into a protected branch SHALL require the build and test workflows to complete successfully as required status checks, so that unverified code cannot be merged.

#### Scenario: Failing checks block the merge

- **WHEN** a pull request's build or test status check is failing or has not completed
- **THEN** the pull request cannot be merged until the required checks pass

#### Scenario: Checks are referenced by stable names

- **WHEN** the required status checks are configured
- **THEN** they reference stable check names exposed by the `build.yml` and `test.yml` workflows so the requirement resolves consistently across runs

### Requirement: Reproducible repository-settings configuration

Because branch protection lives in GitHub repository settings outside the workflow files, the change SHALL capture the required rules as a reproducible, documented configuration (e.g. a `gh api` script and accompanying documentation) so the settings can be applied and audited without manual clicking.

#### Scenario: Settings can be reapplied from the repository

- **WHEN** an administrator needs to (re)apply branch protection
- **THEN** a committed script/documentation describes the exact required rules (no direct push, required review, required build/test checks) and can be executed to set them
