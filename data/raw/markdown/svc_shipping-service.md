---
title: Shipping Service
owner: Logistics
last_updated: 2024-04-18
---

# Shipping Service

Owner: **Logistics** · Tech lead: Chloe Dubois

Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Container images are built once and promoted across environments by digest. Database schema migrations must be backward compatible for at least one release.

## Deployment

To deploy shipping-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/shipping-service/values-prod.yaml`. Then sync the ArgoCD application `shipping-service-prod`
(`argocd app sync shipping-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/health`. Secrets must never be committed; the pre-commit hook scans for high-entropy strings.

## On-call

Page the on-call engineer via PagerDuty service "Shipping Service". Discussion happens in `#logistics-oncall`.

## Notes

On-call handover happens every Monday at 10:00 local time. Capacity planning for the holiday peak starts in September every year. Feature work is paused during incident follow-up weeks until action items are closed. All services must expose Prometheus metrics on the /metrics path.
