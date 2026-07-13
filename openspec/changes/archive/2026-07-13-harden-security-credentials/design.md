## Context

EnergyHub is fully built, containerized (Fase 14), decomposed into microservices (Fase 15), orchestrated on Kubernetes (Fase 16), and continuously delivered (Fase 17). Throughout, credentials and dev surfaces were left at their defaults because everything ran locally. The concrete debt today is:

- **JWT `SECRET_KEY`** defaults to `"change-me-in-production"` in `energyhub/src/energyhub/config/settings.py` (and each `services/*/src/energyhub/config.py`), and the same string is committed in `k8s/secret.yaml`. The gateway and every service share this key (auth signs, the rest validate), so a leaked key forges any identity.
- **Seeded admin** is created by the seed migration with a committed bcrypt hash of the published password `ChangeMe123!` (username `admin`).
- **Grafana** ships `GF_SECURITY_ADMIN_USER=admin` / `GF_SECURITY_ADMIN_PASSWORD=admin` in `docker-compose.yml`.
- **Postgres/RabbitMQ** use `energyhub123` in `docker-compose.yml` and inside the credential-embedding URLs in `k8s/secret.yaml`.
- **`k8s/secret.yaml`** commits all of the above as `stringData` (base64 at rest in etcd, plaintext in the repo) — its own header already flags this as a pre-production risk.
- **`/internal/*`** routers (Fase 15) are unauthenticated by design, relying solely on not being published by the gateway.
- **Traefik** runs `api.dashboard: true` with `insecure: true`; **Consul** runs with `-ui` on a ClusterIP.
- **Edge traffic** is plain HTTP (`http://energyhub.local`); there are **no NetworkPolicies**.

The constraints are fixed by earlier phases: one image and one `config.py` per service, a shared `SECRET_KEY` contract across services, the credential-embedding `DATABASE_URL`/`RABBITMQ_URL` shape, and the Fase 16 manifest layout under `k8s/`. This change is security hardening — configuration, manifests, a migration tweak, and a small startup guard — with no domain/feature behavior change. Its guiding rule (project owner's standing constraint): **security fixes precede any non-local deployment**.

## Goals / Non-Goals

**Goals:**
- Remove every committed placeholder/default credential and source each from an environment variable or secret, with no committed default value.
- Make a `production` profile fail fast at startup when any credential is still a known default/placeholder.
- Replace the plaintext committed Kubernetes `Secret` with an encrypted (SealedSecret) or externalized (ExternalSecret/Vault) representation, and guard against committing plaintext secrets in CI.
- Require authentication and/or restriction for the `/internal/*` endpoints, the Traefik dashboard, and the Consul UI, and keep them off the public edge.
- Terminate TLS at the `Ingress` (cert-manager) and redirect HTTP→HTTPS.
- Segment pod-to-pod traffic with default-deny + least-privilege NetworkPolicies.
- Document a credential-rotation runbook.

**Non-Goals:**
- No new product features, domain behavior, or API surface — auth/JWT semantics (Fase 7) and the inter-service HTTP-client contract (Fase 15) are unchanged.
- No change to which values are sensitive or to the credential-embedding URL shape (Fase 16 contract preserved); only how they are supplied and protected changes.
- No full secrets-platform buildout (HA Vault cluster, dynamic DB credentials, automatic rotation loops) — a single sealing/external-store mechanism is enough for now.
- No mutual-TLS mesh between pods; edge TLS plus NetworkPolicy segmentation is the target, not in-cluster mTLS.
- No SSO/OIDC for Grafana/Traefik/Consul — strong rotated static credentials and non-exposure suffice for this iteration.

## Decisions

**Credentials come from the environment/secrets with no committed default:**
- **Decision:** Change `SECRET_KEY`, the database and RabbitMQ passwords, and the Grafana admin credentials to required settings with no in-code default; supply them via env vars locally and via the Kubernetes `Secret` in the cluster.
- **Rationale:** A committed default is a credential — even "change me" strings get shipped. Making them required means an unset value is a loud failure rather than a silent insecure default.
- **Alternative considered:** Keep placeholder defaults and rely on documentation to change them — rejected; the current state is exactly that failure mode.

**A production profile guard fails fast on default values:**
- **Decision:** On startup, when `environment == "production"`, validate that no required credential equals a known placeholder (`change-me-in-production`, `energyhub123`, `admin`, `ChangeMe123!`) and that none is empty; raise and abort boot otherwise.
- **Rationale:** Defense against the most likely mistake — deploying with a leftover default. Failing fast at boot is safer than discovering it after exposure. Local/dev profiles keep working with convenient defaults.
- **Alternative considered:** Warn-only logging — rejected; a warning does not stop an insecure production process from serving traffic.

**Seeded admin password is derived from a deploy-time secret and must be rotated:**
- **Decision:** The seed migration reads the admin password (or its hash) from a deploy-time secret/env var instead of embedding a committed hash of `ChangeMe123!`, and the account is flagged to require rotation on first use outside local dev.
- **Rationale:** The published hash lets anyone log in as admin on a fresh deploy. Deriving it from a secret removes the committed credential; forced rotation prevents a shared bootstrap password from persisting.
- **Alternative considered:** Delete the admin seed and require manual creation — rejected; a deterministic bootstrap admin is needed for first-boot RBAC and the k8s e2e seed, so we keep the seed but de-risk the credential.

**Sealed Secrets as the default committed-secret mechanism, with External Secrets/Vault as the alternative:**
- **Decision:** Replace the plaintext `k8s/secret.yaml` with a `SealedSecret` (Bitnami controller decrypts it in-cluster into the real `Secret`) as the default, and document an External Secrets Operator + Vault path for teams that already run a secret store. Keep the resolved `Secret` keys identical so `valueFrom.secretKeyRef` consumers are untouched.
- **Rationale:** Sealed Secrets keeps the GitOps "everything in the repo" model while making the committed artifact safe (asymmetrically encrypted; only the in-cluster controller can decrypt). External Secrets/Vault suits teams with an existing store but adds a runtime dependency. Isolating the choice to how the `Secret` is produced avoids forking manifests.
- **Alternative considered:** SOPS-encrypted files — viable but adds a decrypt step to the deploy path; committing raw `Secret`s and relying on etcd encryption — rejected, because it leaves plaintext in git history.

**`/internal/*` requires an inter-service credential in addition to network isolation:**
- **Decision:** Require a shared inter-service secret (header/token) on `/internal/*` and pair it with a NetworkPolicy that only admits the calling services; keep these routes off the public gateway.
- **Rationale:** "Not published by the gateway" is a single point of failure — a routing mistake or a pod on the same network could reach unauthenticated user lookups. Requiring a credential is defense-in-depth on top of L3/L4 restriction.
- **Alternative considered:** NetworkPolicy alone — rejected as single-layer; full mTLS between services — deferred as a larger mesh change beyond this iteration.

**Disable insecure admin UIs and keep them internal:**
- **Decision:** Turn off Traefik's `insecure` dashboard and require authentication (e.g. a basic-auth middleware) for it; drop the Consul `-ui`/exposure or restrict it, and keep both off any public route, backed by NetworkPolicy.
- **Rationale:** An open dashboard/UI exposes routing topology and service health to anyone who can reach the port. These are operator tools, not public surfaces.
- **Alternative considered:** Leave them internal-only without auth — rejected; internal networks are not a trust boundary once the cluster hosts real data.

**TLS terminates at the Ingress via cert-manager:**
- **Decision:** Add cert-manager with an issuer and a TLS-enabled `Ingress` that terminates HTTPS at the edge and redirects HTTP→HTTPS; the gateway continues to receive in-cluster traffic.
- **Rationale:** Edge termination is the lowest-friction way to encrypt external traffic and integrates with the existing `Ingress` from Fase 16; cert-manager automates issuance/renewal.
- **Alternative considered:** Per-service TLS / in-cluster mTLS — deferred (mesh-scale change); manual certs — rejected as unmanaged and prone to expiry.

**Default-deny NetworkPolicies with explicit allow rules:**
- **Decision:** Apply a namespace default-deny ingress policy plus per-service allow rules that permit only declared dependencies (gateway→services, services→auth `/internal`, services→Postgres/RabbitMQ/Consul, scrapers→metrics).
- **Rationale:** Least privilege limits blast radius if a pod is compromised and directly backs the internal/admin surface lockdown.
- **Alternative considered:** No policies (current state) — rejected; allow-all is the opposite of least privilege.

## Risks / Trade-offs

- **Rotating shared `SECRET_KEY` invalidates existing tokens** → Coordinate rotation as a brief re-auth event; document it in the runbook and roll all services together since they share the key.
- **A wrong sealing/store key makes secrets unrecoverable** → Back up the Sealed Secrets controller private key (or the Vault unseal/root material) outside the repo; document restore in the runbook. Losing it, not leaking it, is the operational hazard.
- **Production guard could block a legitimate boot** (e.g. a real password that happens to look weak) → The guard only rejects the explicit known-placeholder set and empty values, not arbitrary weak strings, to avoid false positives.
- **Adding controllers (Sealed Secrets/External Secrets, cert-manager) grows the platform's moving parts** → Pin versions, document install order, and treat them as prerequisites verified before deploy — mirroring how Fase 16 gated on the ingress/metrics addons.
- **NetworkPolicies can silently break traffic if a dependency is missed** → Roll out default-deny last, after allow rules are in place and validated; keep a documented policy-to-dependency map so a broken call maps to a missing rule.
- **`/internal` credential adds a shared secret to manage** → It is stored and rotated exactly like the other secrets (sealed/externalized), so it inherits the same protection rather than becoming a new plaintext value.
- **Cannot be fully validated without a non-local cluster** → Manifests and guards are authored to the plan and validated for syntax/behavior locally (e.g. the production guard is unit-testable); end-to-end TLS/policy validation happens once the target cluster and DNS are wired.

## Migration Plan

1. Make `SECRET_KEY`, DB/RabbitMQ passwords, and Grafana admin credentials required (no committed default) in `settings.py`, each `services/*/config.py`, and `docker-compose.yml`; supply values via `.env` locally.
2. Add the production-profile startup guard and unit-test it against the known-placeholder set.
3. Update the seed migration to derive the admin password from a deploy-time secret and flag first-use rotation; keep the downgrade path intact.
4. Install the secret controller (Sealed Secrets default, or External Secrets Operator + Vault), generate fresh credential values out of band, and produce the sealed/external representation replacing `k8s/secret.yaml`; add the CI guard that fails on committed plaintext secrets.
5. Disable Traefik `insecure` and add dashboard auth; remove/restrict the Consul UI and exposure; require the inter-service credential on `/internal/*`.
6. Install cert-manager + issuer and switch the `Ingress` to terminate TLS with HTTP→HTTPS redirect.
7. Add per-service allow NetworkPolicies, validate all flows, then apply the namespace default-deny policy last.
8. Write the credential-rotation runbook (per-credential steps + sealing/store key backup/restore).
9. Rollback of the change itself: the guards and required settings are additive; reverting to the previous manifests/settings restores prior behavior, but any rotated credential stays rotated (the old defaults must not be reintroduced).

## Open Questions

- Is Sealed Secrets the canonical mechanism for this repo, or does the team already run Vault/External Secrets that should be the default instead?
- Should the `/internal/*` credential be a static shared secret for now, or should this iteration move directly to mTLS between services?
- Which issuer backs cert-manager for the target environment — a public ACME (Let's Encrypt) for a real domain, or an internal CA for private/staging clusters?
- Should the production guard extend to non-credential hardening (e.g. refusing `insecure` Traefik, refusing an exposed Consul UI) as declarative preflight checks, or stay scoped to credentials?
- Does the target cluster's CNI enforce NetworkPolicy (some default CNIs ignore it), and if not, which CNI is standardized before default-deny is applied?
