---
title: Inventory Service
owner: Supply Chain
last_updated: 2024-09-23
---

# Inventory Service

Owner: **Supply Chain** · Tech lead: Grace Kim

Capacity planning for the holiday peak starts in September every year. Database schema migrations must be backward compatible for at least one release. The dashboards were updated to show saturation alongside latency and errors.

## Deployment

To deploy inventory-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/inventory-service/values-prod.yaml`. Then sync the ArgoCD application `inventory-service-prod`
(`argocd app sync inventory-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/healthz`. Container images are built once and promoted across environments by digest.

## On-call

Page the on-call engineer via PagerDuty service "Inventory Service". Discussion happens in `#supply-oncall`.

## Notes

Postmortems are blameless and are published within five business days. Database schema migrations must be backward compatible for at least one release. Capacity planning for the holiday peak starts in September every year. Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
