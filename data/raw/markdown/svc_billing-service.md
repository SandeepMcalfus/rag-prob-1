---
title: Billing Service
owner: Finance Engineering
last_updated: 2024-03-27
---

# Billing Service

Owner: **Finance Engineering** · Tech lead: Noah Fischer

All services must expose Prometheus metrics on the /metrics path. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. We should revisit the alert thresholds after the next game day.

## Deployment

To deploy billing-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/billing-service/values-prod.yaml`. Then sync the ArgoCD application `billing-service-prod`
(`argocd app sync billing-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/status`. All services must expose Prometheus metrics on the /metrics path.

## On-call

Page the on-call engineer via PagerDuty service "Billing Service". Discussion happens in `#fin-eng-oncall`.

## Notes

Staging mirrors production topology but runs at roughly one tenth of the capacity. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Feature work is paused during incident follow-up weeks until action items are closed. Service-level objectives are reviewed quarterly with product owners.
