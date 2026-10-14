---
title: Database Migration Policy
last_updated: 2024-02-11
---

# Database Migration Policy

Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Postmortems are blameless and are published within five business days. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.

## Background

Load tests should be coordinated in the platform channel so they do not trip alerts. Service-level objectives are reviewed quarterly with product owners. Container images are built once and promoted across environments by digest. All services must expose Prometheus metrics on the /metrics path. On-call handover happens every Monday at 10:00 local time.

## Guidance

- On-call handover happens every Monday at 10:00 local time.
- Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
- All services must expose Prometheus metrics on the /metrics path.
- Infrastructure changes go through Terraform plans that need two approvals.
- Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
- Postmortems are blameless and are published within five business days.

## FAQ

We should revisit the alert thresholds after the next game day. Infrastructure changes go through Terraform plans that need two approvals. Postmortems are blameless and are published within five business days.
