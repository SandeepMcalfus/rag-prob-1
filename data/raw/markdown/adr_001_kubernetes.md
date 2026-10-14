---
title: ADR 001: Adopt Kubernetes
last_updated: 2025-03-15
---

# ADR 001: Adopt Kubernetes

Infrastructure changes go through Terraform plans that need two approvals. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Infrastructure changes go through Terraform plans that need two approvals.

## Background

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Staging mirrors production topology but runs at roughly one tenth of the capacity. Every service has a README that links to its dashboards and runbook. Infrastructure changes go through Terraform plans that need two approvals. Database schema migrations must be backward compatible for at least one release.

## Guidance

- Capacity planning for the holiday peak starts in September every year.
- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Every service has a README that links to its dashboards and runbook.
- All services must expose Prometheus metrics on the /metrics path.
- On-call handover happens every Monday at 10:00 local time.

## FAQ

Postmortems are blameless and are published within five business days. Infrastructure changes go through Terraform plans that need two approvals. Every service has a README that links to its dashboards and runbook.
