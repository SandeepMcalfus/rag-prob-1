---
title: Analytics Pipeline
owner: Data Platform
last_updated: 2024-11-11
---

# Analytics Pipeline

Owner: **Data Platform** · Tech lead: Emma Larsen

All services must expose Prometheus metrics on the /metrics path. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Every service has a README that links to its dashboards and runbook.

## Deployment

To deploy analytics-pipeline to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/analytics-api/values-prod.yaml`. Then sync the ArgoCD application `analytics-api-prod`
(`argocd app sync analytics-api-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/ping`. The dashboards were updated to show saturation alongside latency and errors.

## On-call

Page the on-call engineer via PagerDuty service "Analytics Pipeline". Discussion happens in `#data-platform-oncall`.

## Notes

Dependency upgrades are batched weekly by the platform bot. Feature work is paused during incident follow-up weeks until action items are closed. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Load tests should be coordinated in the platform channel so they do not trip alerts.
