## MODIFIED Requirements

### Requirement: Data survives container recreation

Data written to a stateful service SHALL persist across a full restart cycle of its runtime — a `docker-compose down` followed by `docker-compose up -d` in Compose, or a pod restart/reschedule in Kubernetes — because it is stored on durable storage (named Docker volumes or Kubernetes PersistentVolumeClaims) rather than on the container's writable layer or an `emptyDir` tied to the pod lifetime.

#### Scenario: Database data persists across a restart cycle

- **WHEN** rows are written to PostgreSQL, then the stack is brought down with `docker-compose down` and back up with `docker-compose up -d`
- **THEN** the previously written rows are still present after restart

#### Scenario: Cache persistence is enabled for Redis

- **WHEN** Redis is configured with append-only persistence and the stack is restarted
- **THEN** keys written before the restart remain available afterward

#### Scenario: Database data persists across a pod restart in the cluster

- **WHEN** rows are written to the in-cluster PostgreSQL, then its pod is deleted and rescheduled by Kubernetes
- **THEN** the replacement pod re-attaches the same PersistentVolumeClaim and the previously written rows are still present

## ADDED Requirements

### Requirement: PersistentVolumeClaims for stateful Kubernetes backends

The in-cluster stateful backends SHALL store their data on PersistentVolumeClaims rather than `emptyDir`, so data is decoupled from the pod lifetime and survives restart and rescheduling. At minimum PostgreSQL (`/var/lib/postgresql/data`) and Kafka (`/var/lib/kafka/data`) MUST be PVC-backed; Redis and RabbitMQ SHALL follow the same pattern. Each claim MUST declare a requested capacity and a `StorageClass` (the cluster default in `dev`, an explicit class in `prod`).

#### Scenario: No stateful backend uses emptyDir

- **WHEN** the rendered Kubernetes manifests for the stateful backends are inspected
- **THEN** their data directories are mounted from PersistentVolumeClaims (or `volumeClaimTemplates`) and none of them mounts an `emptyDir` at its data path

#### Scenario: Claim binds to a volume before the pod runs

- **WHEN** a stateful backend's manifests are applied to a cluster with a usable `StorageClass`
- **THEN** its PersistentVolumeClaim binds to a provisioned volume and the pod mounts it at the declared data path

#### Scenario: Postgres data path is preserved

- **WHEN** the PostgreSQL PVC is mounted
- **THEN** it is mounted at `/var/lib/postgresql/data` so the existing `PGDATA=/var/lib/postgresql/data/pgdata` subdirectory and initdb flow continue to work
