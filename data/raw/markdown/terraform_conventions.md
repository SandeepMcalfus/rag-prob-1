---
title: Terraform Conventions
last_updated: 2025-12-24
---

# Terraform Conventions

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Capacity planning for the holiday peak starts in September every year. Load tests should be coordinated in the platform channel so they do not trip alerts.

## Background

All services must expose Prometheus metrics on the /metrics path. The dashboards were updated to show saturation alongside latency and errors. Service-level objectives are reviewed quarterly with product owners. Every service has a README that links to its dashboards and runbook. Staging mirrors production topology but runs at roughly one tenth of the capacity.

## Guidance

- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Staging mirrors production topology but runs at roughly one tenth of the capacity.
- Staging mirrors production topology but runs at roughly one tenth of the capacity.
- Every service has a README that links to its dashboards and runbook.
- Service-level objectives are reviewed quarterly with product owners.

## FAQ

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Service-level objectives are reviewed quarterly with product owners. Remember to tag pull requests with the owning team so reviews get routed correctly.
