## ADDED Requirements

### Requirement: Host resource gauges

The system SHALL expose host resource usage as Prometheus gauges, including memory usage in bytes, CPU usage percentage, and disk usage percentage, collected via `psutil`.

#### Scenario: Resource gauges are published

- **WHEN** the metrics are scraped
- **THEN** the `memory_usage_bytes`, `cpu_usage_percent`, and `disk_usage_percent` gauges are present with current host values

### Requirement: Resource metric refresh

The system SHALL refresh the host resource gauges so their values reflect the host state at collection time rather than a stale startup snapshot.

#### Scenario: Values updated before scrape

- **WHEN** a scrape triggers resource metric collection
- **THEN** the resource gauges are updated from `psutil` so they reflect the current memory, CPU, and disk usage
