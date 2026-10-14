---
title: User Profile Service
owner: Customer Data
last_updated: 2024-06-30
---

# User Profile Service

Owner: **Customer Data** · Tech lead: Hannah Weber

Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Staging mirrors production topology but runs at roughly one tenth of the capacity. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.

## Deployment

To deploy user-profile-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/user-profile-service/values-prod.yaml`. Then sync the ArgoCD application `user-profile-service-prod`
(`argocd app sync user-profile-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/actuator/health`. Service-level objectives are reviewed quarterly with product owners.

## On-call

Page the on-call engineer via PagerDuty service "User Profile Service". Discussion happens in `#customer-data-oncall`.

## Notes

Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Dependency upgrades are batched weekly by the platform bot. Service-level objectives are reviewed quarterly with product owners. The dashboards were updated to show saturation alongside latency and errors.
