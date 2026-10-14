---
title: Engineering Onboarding
last_updated: 2023-01-01
---

# Engineering Onboarding

Staging mirrors production topology but runs at roughly one tenth of the capacity. We should revisit the alert thresholds after the next game day. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.

## Background

Service-level objectives are reviewed quarterly with product owners. All services must expose Prometheus metrics on the /metrics path. Postmortems are blameless and are published within five business days. Service-level objectives are reviewed quarterly with product owners. The dashboards were updated to show saturation alongside latency and errors.

## Guidance

- Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
- On-call handover happens every Monday at 10:00 local time.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Container images are built once and promoted across environments by digest.
- Staging mirrors production topology but runs at roughly one tenth of the capacity.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.

## FAQ

On-call handover happens every Monday at 10:00 local time. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
