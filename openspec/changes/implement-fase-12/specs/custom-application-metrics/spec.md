## ADDED Requirements

### Requirement: Centralized metrics factory

The system SHALL provide a `MetricsConfig` factory in `shared/infrastructure/metrics/` that exposes the custom Prometheus collectors — counters, gauges, and histograms — used across the application, so collectors are defined in one place and reused rather than re-declared.

#### Scenario: Factory exposes reusable collectors

- **WHEN** a service requests a collector such as the client-created counter or the request-duration histogram from `MetricsConfig`
- **THEN** it receives the corresponding Prometheus collector configured with the correct metric name, help text, and labels

### Requirement: Business event metrics

The system SHALL record business events as Prometheus metrics, including clients created, contracts created labeled by status, invoices paid, and the number of active clients as a gauge.

#### Scenario: Client creation increments its counter

- **WHEN** a client is successfully created
- **THEN** the `client_created_total` counter is incremented by one

#### Scenario: Contract creation labeled by status

- **WHEN** a contract is created with a given status
- **THEN** the `contract_created_total` counter is incremented for that status label

#### Scenario: Active clients gauge reflects current count

- **WHEN** the active-clients count is updated
- **THEN** the `clients_active` gauge is set to the current number of active clients

### Requirement: Operation duration instrumentation

The system SHALL record the duration of instrumented service operations in a Prometheus histogram labeled by endpoint and method.

#### Scenario: Operation duration observed

- **WHEN** an instrumented service operation executes
- **THEN** its elapsed time is observed in the request-duration histogram under the operation's endpoint and method labels

### Requirement: Business metrics initialization

The system SHALL initialize labeled business counters and gauges to zero at startup so that series exist before the first event and dashboards render without missing data.

#### Scenario: Counters initialized at zero

- **WHEN** the application starts and no business events have occurred
- **THEN** the labeled business counters and gauges are present with a value of zero
