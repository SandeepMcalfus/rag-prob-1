---
title: Payment Service
owner: Payments Core
last_updated: 2024-10-01
---

# Payment Service

Owner: **Payments Core** · Tech lead: Priya Nair

Container images are built once and promoted across environments by digest. Remember to tag pull requests with the owning team so reviews get routed correctly. Feature work is paused during incident follow-up weeks until action items are closed.

## Deployment

To deploy payment-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/payment-service/values-prod.yaml`. Then sync the ArgoCD application `payment-service-prod`
(`argocd app sync payment-service-prod`) and watch the rollout in the ArgoCD UI.

### Release strategy

Production uses Argo Rollouts canary releases with automated analysis on error rate.

## Health checks

Liveness and readiness probes hit `/actuator/health`. Container images are built once and promoted across environments by digest.

## On-call

Page the on-call engineer via PagerDuty service "Payment Service". Discussion happens in `#payments-oncall`.

## Notes

Infrastructure changes go through Terraform plans that need two approvals. All services must expose Prometheus metrics on the /metrics path. Load tests should be coordinated in the platform channel so they do not trip alerts. Database schema migrations must be backward compatible for at least one release.
