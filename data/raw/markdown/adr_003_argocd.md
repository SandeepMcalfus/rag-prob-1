---
title: ADR 003: GitOps with ArgoCD
last_updated: 2024-05-02
---

# ADR 003: GitOps with ArgoCD

Infrastructure changes go through Terraform plans that need two approvals. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. On-call handover happens every Monday at 10:00 local time.

## Background

Staging mirrors production topology but runs at roughly one tenth of the capacity. Remember to tag pull requests with the owning team so reviews get routed correctly. Feature work is paused during incident follow-up weeks until action items are closed. Infrastructure changes go through Terraform plans that need two approvals. Feature work is paused during incident follow-up weeks until action items are closed.

## Guidance

- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- Capacity planning for the holiday peak starts in September every year.
- We should revisit the alert thresholds after the next game day.
- The dashboards were updated to show saturation alongside latency and errors.
- Feature work is paused during incident follow-up weeks until action items are closed.
- Dependency upgrades are batched weekly by the platform bot.

## FAQ

On-call handover happens every Monday at 10:00 local time. Remember to tag pull requests with the owning team so reviews get routed correctly. Load tests should be coordinated in the platform channel so they do not trip alerts.
