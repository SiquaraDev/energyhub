## ADDED Requirements

### Requirement: Bounded contexts are identified from existing modules

The system SHALL define a bounded context for each cohesive area of the current monolith — Auth, Clients, Contracts, Negotiations, Financial, Audit, Notifications, and Reports — with each context assigned a single target service that owns its data and behavior.

#### Scenario: Every module maps to exactly one context

- **WHEN** the module inventory is reviewed against the target service list
- **THEN** each module is assigned to exactly one bounded context, and no module is left unassigned or split across two owning services

### Requirement: Inter-context dependency graph is defined

The system SHALL document the dependency direction between contexts — Auth as independent, Clients depending on Auth, Contracts depending on Auth and Clients, Negotiations depending on Auth and Contracts, Financial depending on Auth and Contracts, and Audit and Notifications as independent event consumers — so extraction order and communication direction are unambiguous.

#### Scenario: Dependencies point only in the declared direction

- **WHEN** a context's dependencies are inspected
- **THEN** it depends only on the contexts declared upstream of it, and no cyclic dependency between two contexts is introduced

#### Scenario: Independent contexts have no synchronous upstream

- **WHEN** the Audit or Notification context is inspected
- **THEN** it is shown to consume events rather than depend synchronously on another context

### Requirement: Bounded contexts are documented

The system SHALL record the bounded contexts, their responsibilities, and their dependency graph in `docs/bounded-contexts.md` so the decomposition is a durable, reviewable artifact.

#### Scenario: Documentation lists every context and its dependencies

- **WHEN** `docs/bounded-contexts.md` is opened
- **THEN** it names each target service, states the responsibility of each, and lists the dependencies of each context
