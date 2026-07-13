# edge-tls-termination Specification

## Purpose
TBD - created by archiving change harden-security-credentials. Update Purpose after archive.
## Requirements
### Requirement: Certificate provisioning via cert-manager

The system SHALL provision TLS certificates for the platform host through cert-manager with a configured issuer, so certificates are issued and renewed automatically rather than managed by hand.

#### Scenario: Certificate is issued for the platform host

- **WHEN** cert-manager and its issuer are installed and a certificate is requested for the platform host
- **THEN** a valid certificate is issued and stored in a `Secret` that the `Ingress` can reference

### Requirement: Ingress terminates TLS

The `Ingress` SHALL terminate TLS for the platform host using the issued certificate, so external traffic to the platform is encrypted.

#### Scenario: External request is served over HTTPS

- **WHEN** an external client requests the platform host over HTTPS
- **THEN** the `Ingress` presents the issued certificate and serves the request over an encrypted connection

### Requirement: Plain HTTP is redirected to HTTPS

The edge SHALL redirect plain HTTP requests for the platform host to HTTPS so unencrypted access is not served.

#### Scenario: HTTP request is redirected

- **WHEN** an external client requests the platform host over plain HTTP
- **THEN** the edge responds with a redirect to the HTTPS URL rather than serving content over HTTP

