## ADDED Requirements

### Requirement: Prometheus alert rules

The system SHALL define Prometheus alert rules in `prometheus/alerts.yml` covering high request latency, high error rate, and low available memory, each with a severity label and descriptive annotations, and Prometheus SHALL load these rules.

#### Scenario: Alert rules loaded

- **WHEN** Prometheus reloads its configuration referencing the rule file
- **THEN** the `HighRequestLatency`, `HighErrorRate`, and `LowMemory` rules appear on the Prometheus rules page

#### Scenario: High latency alert fires

- **WHEN** the 95th-percentile request latency exceeds the configured threshold for the rule's `for` duration
- **THEN** the `HighRequestLatency` alert transitions to firing with its `warning` severity and annotations

#### Scenario: High error rate alert fires

- **WHEN** the rate of 5xx responses exceeds the configured threshold for the rule's `for` duration
- **THEN** the `HighErrorRate` alert transitions to firing with its `critical` severity

### Requirement: Alertmanager service

The system SHALL run an Alertmanager Docker Compose service configured via `prometheus/alertmanager.yml`, and Prometheus SHALL forward firing alerts to it.

#### Scenario: Alertmanager receives alerts

- **WHEN** an alert rule is firing in Prometheus
- **THEN** Prometheus routes the alert to the Alertmanager service defined in its `alerting` configuration

### Requirement: Notification receivers

The system SHALL define at least one Alertmanager receiver and route so that firing alerts are dispatched to a notification channel such as email, Slack, or webhook.

#### Scenario: Firing alert dispatched to receiver

- **WHEN** Alertmanager processes a firing alert matching the configured route
- **THEN** it dispatches a notification through the route's receiver
