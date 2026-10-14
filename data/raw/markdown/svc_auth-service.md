---
title: Auth Service
owner: Identity Platform
last_updated: 2024-08-12
---

# Auth Service

Owner: **Identity Platform** · Tech lead: Sofia Marquez

Service-level objectives are reviewed quarterly with product owners. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.

## Deployment

To deploy auth-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/auth-service/values-prod.yaml`. Then sync the ArgoCD application `auth-service-prod`
(`argocd app sync auth-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/health/ready`. Database schema migrations must be backward compatible for at least one release.

## On-call

Page the on-call engineer via PagerDuty service "Auth Service". Discussion happens in `#identity-oncall`.

## Notes

Capacity planning for the holiday peak starts in September every year. Service-level objectives are reviewed quarterly with product owners. Infrastructure changes go through Terraform plans that need two approvals. On-call handover happens every Monday at 10:00 local time.
