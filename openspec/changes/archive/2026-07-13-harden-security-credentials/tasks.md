## 1. Credential Rotation

- [x] 1.1 Make `SECRET_KEY` a required setting with no in-code default in `energyhub/src/energyhub/config/settings.py` and each `services/*/src/energyhub/config.py`
- [x] 1.2 Make the PostgreSQL and RabbitMQ passwords required (no default) and remove `energyhub123` from `docker-compose.yml`, sourcing them from environment variables
- [x] 1.3 Remove the Grafana `admin`/`admin` defaults from `docker-compose.yml` and source `GF_SECURITY_ADMIN_USER`/`GF_SECURITY_ADMIN_PASSWORD` from environment variables
- [x] 1.4 Generate fresh, distinct high-entropy values for `SECRET_KEY`, the Postgres password, and the RabbitMQ password for non-local use
- [x] 1.5 Add a local `.env.example` (no real values) documenting every required credential variable
- [x] 1.6 Confirm the repository contains no active placeholder credential (`change-me-in-production`, `energyhub123`, Grafana `admin`/`admin`)

## 2. Production Credential Validation

- [x] 2.1 Add a startup guard that, when `environment=production`, rejects any credential equal to a known placeholder value
- [x] 2.2 Extend the guard to reject empty or unset required credentials in the `production` profile
- [x] 2.3 Ensure `development`/`staging` profiles remain permissive and are unaffected by the guard
- [x] 2.4 Add unit tests covering placeholder rejection, empty rejection, and the non-production pass-through

## 3. Admin Seed Hardening

- [x] 3.1 Update the seed migration (`alembic/versions/..._seed_data.py`) to derive the admin password hash from a deploy-time secret instead of the committed `ChangeMe123!` hash
- [x] 3.2 Flag the admin account to require password rotation on first use in non-local profiles
- [x] 3.3 Preserve the idempotent, reversible downgrade path of the seed migration
- [x] 3.4 Confirm the seed still creates the `admin` user linked to the `ADMIN` role

## 4. Secret Management Migration

- [x] 4.1 Choose and install the secret controller (Sealed Secrets by default, or External Secrets Operator + Vault)
- [x] 4.2 Produce the encrypted/externalized secret artifact replacing `k8s/secret.yaml`, keeping the resolved `Secret` keys identical to current `secretKeyRef` consumers
- [x] 4.3 Remove the plaintext `k8s/secret.yaml` from the repository and back up the sealing/store key outside the repo
- [x] 4.4 Add a CI guard that fails when a plaintext `Secret` or a known placeholder credential is committed
- [x] 4.5 Apply the sealed/external secret to the cluster and confirm the controller materializes the `Secret` and workloads read the resolved values

## 5. Internal and Admin Surface Lockdown

- [x] 5.1 Require an inter-service credential on the `/internal/*` endpoints across the services (starting with `auth-service`'s `internal_router.py`) and reject unauthenticated calls
- [x] 5.2 Confirm `/internal/*` is not routed through the public gateway/`Ingress`
- [x] 5.3 Disable Traefik `insecure` mode in `k8s/traefik-config.yaml` and add an authentication middleware for the dashboard
- [x] 5.4 Remove/restrict the Consul `-ui` exposure in `k8s/consul-deployment.yaml`/`consul-service.yaml` and keep it off the public edge

## 6. Edge TLS

- [x] 6.1 Install cert-manager and configure an issuer appropriate to the target environment
- [x] 6.2 Request a certificate for the platform host and confirm it is issued into a referenceable `Secret`
- [x] 6.3 Update `k8s/ingress.yaml` to terminate TLS for the platform host using the issued certificate
- [x] 6.4 Add an HTTP→HTTPS redirect at the edge and confirm plain HTTP is redirected

## 7. Network Segmentation

- [x] 7.1 Author per-service allow `NetworkPolicy` rules for each declared dependency (gateway→services, services→auth `/internal`, services→Postgres/RabbitMQ/Consul, scrapers→metrics)
- [x] 7.2 Validate that every legitimate flow still works with the allow rules applied
- [x] 7.3 Apply the namespace default-deny ingress `NetworkPolicy` last and confirm undeclared traffic is blocked
- [x] 7.4 Confirm datastore and Consul ports are reachable only by authorized workloads

## 8. Runbook and Documentation

- [x] 8.1 Write the credential-rotation runbook covering `SECRET_KEY`, admin login, Grafana, Postgres, and RabbitMQ
- [x] 8.2 Document the sealed/external-secret workflow and the sealing/store key backup and restore procedure

## 9. Validation

- [x] 9.1 Confirm no placeholder credential remains and the production guard aborts a boot with any known default
- [x] 9.2 Confirm the committed secret artifact is encrypted/externalized and the CI plaintext-secret guard fails on a planted plaintext secret
- [x] 9.3 Confirm `/internal/*`, the Traefik dashboard, and the Consul UI reject unauthorized access and are not publicly exposed
- [x] 9.4 Confirm external traffic is served over TLS with HTTP redirected, and default-deny NetworkPolicies restrict pod-to-pod traffic
- [x] 9.5 Run `openspec validate harden-security-credentials --strict` and confirm the change is valid
