## ADDED Requirements

### Requirement: Cache invalidation helpers

The system SHALL provide invalidation helpers in `shared/infrastructure/cache/` — `invalidate_cache(namespace, key=None)` to evict a single key or an entire namespace, and `invalidate_all_cache()` to clear the whole cache backend.

#### Scenario: Invalidate a single key

- **WHEN** `invalidate_cache` is called with a namespace and a specific key
- **THEN** only that key is removed from the cache and other keys in the namespace remain

#### Scenario: Invalidate an entire namespace

- **WHEN** `invalidate_cache` is called with a namespace and no key
- **THEN** all entries under that namespace are removed

#### Scenario: Clear all caches

- **WHEN** `invalidate_all_cache` is called
- **THEN** every entry across all namespaces is removed from the backend

### Requirement: Write operations invalidate affected entries

Service write operations (`create`, `update`, `delete`) SHALL invalidate the cache entries affected by the mutation so cached reads never return data that contradicts the database.

#### Scenario: Create evicts list caches

- **WHEN** an entity is created through a service
- **THEN** the affected list/collection cache entries for that domain are invalidated so the next read reflects the new entity

#### Scenario: Update evicts the entity's cached entries

- **WHEN** an entity is updated through a service
- **THEN** the cached entries keyed by that entity's identifiers (such as id and cnpj) are invalidated

#### Scenario: Delete evicts the entity's cached entries

- **WHEN** an entity is deleted through a service
- **THEN** the cached entries for that entity are invalidated so a subsequent read does not return the removed entity
