---
title: Coding Standards
last_updated: 2024-02-08
---

# Coding Standards

Every service has a README that links to its dashboards and runbook. Postmortems are blameless and are published within five business days. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.

## Background

Service-level objectives are reviewed quarterly with product owners. The dashboards were updated to show saturation alongside latency and errors. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. We should revisit the alert thresholds after the next game day. Tracing uses OpenTelemetry with a ten percent head-based sampling rate.

## Guidance

- Database schema migrations must be backward compatible for at least one release.
- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- Container images are built once and promoted across environments by digest.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Remember to tag pull requests with the owning team so reviews get routed correctly.
- Staging mirrors production topology but runs at roughly one tenth of the capacity.

## FAQ

On-call handover happens every Monday at 10:00 local time. Staging mirrors production topology but runs at roughly one tenth of the capacity. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
