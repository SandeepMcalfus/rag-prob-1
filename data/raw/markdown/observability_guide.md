---
title: Observability Guide
last_updated: 2023-07-16
---

# Observability Guide

Feature work is paused during incident follow-up weeks until action items are closed. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Load tests should be coordinated in the platform channel so they do not trip alerts.

## Background

Capacity planning for the holiday peak starts in September every year. Load tests should be coordinated in the platform channel so they do not trip alerts. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Database schema migrations must be backward compatible for at least one release. On-call handover happens every Monday at 10:00 local time.

## Guidance

- Staging mirrors production topology but runs at roughly one tenth of the capacity.
- Load tests should be coordinated in the platform channel so they do not trip alerts.
- On-call handover happens every Monday at 10:00 local time.
- Tracing uses OpenTelemetry with a ten percent head-based sampling rate.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Database schema migrations must be backward compatible for at least one release.

## FAQ

Load tests should be coordinated in the platform channel so they do not trip alerts. All services must expose Prometheus metrics on the /metrics path. Dependency upgrades are batched weekly by the platform bot.
