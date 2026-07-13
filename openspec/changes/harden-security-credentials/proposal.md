## Why

The platform reached milestone 1.0.0 with every credential still set to a committed placeholder and several operational surfaces left open for local development. The JWT `SECRET_KEY` is `change-me-in-production`, the seeded admin logs in with the publicly-known `admin` / `ChangeMe123!`, Grafana ships `admin` / `admin`, the Postgres and RabbitMQ passwords are `energyhub123`, and the Kubernetes `Secret` commits all of them as base64 plaintext in `k8s/secret.yaml`. On top of that, the microservices' `/internal/*` endpoints are unauthenticated by design, the Traefik dashboard runs `insecure: true`, the Consul UI is enabled, external traffic is plain HTTP, and there are no NetworkPolicies. Per the project owner's standing constraint, these placeholder credentials and open dev surfaces are a critical risk that must be closed **before any non-local or production deployment** — this change closes them.

## What Changes

- Rotate every placeholder/default credential and remove it from committed files: the JWT `SECRET_KEY` (`energyhub/src/energyhub/config/settings.py` and each `services/*/src/energyhub/config.py`), the Grafana `admin`/`admin` (`docker-compose.yml`), and the Postgres and RabbitMQ passwords (`energyhub123`, in `docker-compose.yml` and `k8s/secret.yaml`). Every credential is sourced from an environment variable or secret with no committed default value.
- Rotate the seeded admin login so its password is no longer a committed known hash: the Fase 4/7 seed migration (`alembic/versions/..._seed_data.py`) derives the admin password hash from a deploy-time secret, and the account must be rotated on first use outside local development.
- Add a **production profile guard**: when `environment=production`, the application fails fast at startup if any credential (`SECRET_KEY`, database URL password, RabbitMQ password, admin password) still holds a known default/placeholder value.
- **BREAKING** (operational): Migrate the committed Kubernetes `Secret` (`k8s/secret.yaml`, today base64 plaintext) to a secret-management approach — Bitnami Sealed Secrets or an External Secrets Operator / HashiCorp Vault integration — so no plaintext secret material is committed to the repository; a CI guard rejects committed plaintext secrets.
- Lock down the internal/admin surfaces that are open in dev: the `/internal/*` endpoints (require an inter-service credential and never route through the public gateway), the Traefik dashboard (disable `insecure`, require authentication), and the Consul UI (not externally exposed, access-controlled), each additionally restricted by NetworkPolicy.
- Enable TLS at the edge: cert-manager issues certificates and the `Ingress` terminates TLS so external traffic is encrypted, with an HTTP→HTTPS redirect.
- Add default-deny NetworkPolicies plus explicit least-privilege allow rules so pod-to-pod traffic is restricted to declared dependencies.
- Document a credential-rotation runbook covering each credential and the sealed/external-secret workflow.

## Capabilities

### New Capabilities

- `credential-rotation`: Rotate the placeholder JWT `SECRET_KEY`, Grafana admin, PostgreSQL, and RabbitMQ credentials; remove committed defaults from source, `docker-compose.yml`, and manifests; source every credential from an environment variable or secret; and document a rotation runbook.
- `production-credential-validation`: When the `production` profile is active, the application refuses to start if any required credential still holds a known default or placeholder value, so a misconfigured deploy fails fast rather than running insecurely.
- `internal-admin-surface-hardening`: The `/internal/*` endpoints, the Traefik dashboard, and the Consul UI require authentication and/or are access-restricted and are never publicly exposed.
- `edge-tls-termination`: cert-manager provisions certificates and the `Ingress` terminates TLS so external traffic is encrypted, redirecting plain HTTP to HTTPS.
- `network-policy-segmentation`: Default-deny NetworkPolicies plus explicit allow rules restrict pod-to-pod traffic to each service's declared dependencies.

### Modified Capabilities

- `configuration-and-secrets`: The committed Kubernetes `Secret` MUST no longer carry plaintext secret material; the committed representation MUST be encrypted (a `SealedSecret`) or externalized (an `ExternalSecret` referencing a secret manager), while workloads still consume the resolved values via `valueFrom.secretKeyRef`.
- `database-seed-data`: The seeded default admin password MUST be derived from a deploy-time secret and rotated on first use in non-local profiles, rather than a committed known bcrypt hash of a published password.

## Impact

- **Consumes / depends on**: Fase 7 (auth, JWT `SECRET_KEY`, admin seed), Fase 12 (Grafana/observability credentials), Fase 15 (`/internal` endpoints, per-service `config.py`, Traefik, Consul), Fase 16 (`k8s/` `Secret`/`ConfigMap`, `Ingress`, Traefik/Consul manifests).
- **Affected files**: `energyhub/src/energyhub/config/settings.py`, `services/*/src/energyhub/config.py`, `alembic/versions/..._seed_data.py`, `docker-compose.yml`, `k8s/secret.yaml`, `k8s/ingress.yaml`, `k8s/traefik-config.yaml`, `k8s/traefik-deployment.yaml`, `k8s/consul-deployment.yaml`, `k8s/consul-service.yaml`, the per-service `/internal` routers (e.g. `services/auth-service/src/energyhub/auth/presentation/router/internal_router.py`), and new NetworkPolicy / TLS / sealed-secret manifests under `k8s/`.
- **New dependencies (operational)**: a secret controller (Bitnami Sealed Secrets *or* External Secrets Operator + a store such as HashiCorp Vault), cert-manager and an ACME/issuer, and a CNI that enforces NetworkPolicy (the Fase 16 cluster's ingress addon assumed present).
- **Provides**: rotated credentials with no committed defaults, a production fail-fast guard, encrypted-at-rest committed secrets, authenticated/restricted internal and admin surfaces, edge TLS, network segmentation, and a rotation runbook.
- **Secrets/coordination**: operators must generate fresh credential values out of band, seal/register them, and store the sealing/store keys outside the repo; the running cluster is the source of truth for the resolved `Secret`, and no plaintext credential is ever committed.
- **Scope boundary**: this is a security-hardening change consumed before non-local use; it does not add product features or alter domain behavior.
