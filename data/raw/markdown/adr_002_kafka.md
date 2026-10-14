---
title: ADR 002: Kafka as event backbone
last_updated: 2023-04-22
---

# ADR 002: Kafka as event backbone

Database schema migrations must be backward compatible for at least one release. We should revisit the alert thresholds after the next game day. Infrastructure changes go through Terraform plans that need two approvals.

## Background

Infrastructure changes go through Terraform plans that need two approvals. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Postmortems are blameless and are published within five business days. On-call handover happens every Monday at 10:00 local time.

## Guidance

- Staging mirrors production topology but runs at roughly one tenth of the capacity.
- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- Tracing uses OpenTelemetry with a ten percent head-based sampling rate.

## FAQ

Dependency upgrades are batched weekly by the platform bot. All services must expose Prometheus metrics on the /metrics path. Remember to tag pull requests with the owning team so reviews get routed correctly.
