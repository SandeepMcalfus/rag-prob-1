---
title: Security Baseline
last_updated: 2023-04-25
---

# Security Baseline

Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Staging mirrors production topology but runs at roughly one tenth of the capacity. We should revisit the alert thresholds after the next game day.

## Background

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Dependency upgrades are batched weekly by the platform bot. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Container images are built once and promoted across environments by digest.

## Guidance

- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Capacity planning for the holiday peak starts in September every year.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- All services must expose Prometheus metrics on the /metrics path.
- Tracing uses OpenTelemetry with a ten percent head-based sampling rate.
- Service-level objectives are reviewed quarterly with product owners.

## FAQ

On-call handover happens every Monday at 10:00 local time. Database schema migrations must be backward compatible for at least one release. Dependency upgrades are batched weekly by the platform bot.
