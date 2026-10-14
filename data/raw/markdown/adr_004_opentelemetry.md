---
title: ADR 004: OpenTelemetry
last_updated: 2025-06-09
---

# ADR 004: OpenTelemetry

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Postmortems are blameless and are published within five business days. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.

## Background

Every service has a README that links to its dashboards and runbook. Dependency upgrades are batched weekly by the platform bot. Every service has a README that links to its dashboards and runbook. Feature work is paused during incident follow-up weeks until action items are closed. Capacity planning for the holiday peak starts in September every year.

## Guidance

- We should revisit the alert thresholds after the next game day.
- Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Feature work is paused during incident follow-up weeks until action items are closed.
- All services must expose Prometheus metrics on the /metrics path.
- Tracing uses OpenTelemetry with a ten percent head-based sampling rate.

## FAQ

Load tests should be coordinated in the platform channel so they do not trip alerts. The dashboards were updated to show saturation alongside latency and errors. Database schema migrations must be backward compatible for at least one release.
