# service-resilience Specification

## Purpose
TBD - created by archiving change implement-fase-15. Update Purpose after archive.
## Requirements
### Requirement: Inter-service calls are bounded by a timeout

Every HTTP client SHALL apply an explicit request timeout so a slow or hung dependency cannot block a caller indefinitely.

#### Scenario: Slow dependency is abandoned at the timeout

- **WHEN** an upstream service does not respond within the configured timeout
- **THEN** the client aborts the request and raises a timeout error rather than waiting without bound

### Requirement: Transient failures are retried with backoff

Inter-service calls SHALL be retried on transient failures using `tenacity` with a bounded number of attempts and exponential backoff between attempts, so momentary faults recover without a manual retry.

#### Scenario: Call succeeds after a transient failure

- **WHEN** an upstream call fails transiently and then succeeds on a subsequent attempt
- **THEN** the client returns the successful result after retrying with increasing wait intervals

#### Scenario: Retries are capped

- **WHEN** an upstream call keeps failing
- **THEN** the client stops after the configured maximum number of attempts rather than retrying forever

### Requirement: Failures are contained with a fallback

When an upstream dependency remains unavailable after retries, the client SHALL apply a defined fallback (for example returning `None` or a safe default) so the failure is contained and does not cascade through the caller.

#### Scenario: Exhausted retries trigger the fallback

- **WHEN** all retry attempts to an upstream service are exhausted
- **THEN** the client returns its defined fallback value instead of propagating an unhandled error that would fail the whole request chain

