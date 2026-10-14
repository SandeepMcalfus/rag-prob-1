---
title: Checkout Service
owner: Checkout Experience
last_updated: 2025-01-15
---

# Checkout Service

Owner: **Checkout Experience** · Tech lead: Daniel Okafor

Infrastructure changes go through Terraform plans that need two approvals. On-call handover happens every Monday at 10:00 local time. Tracing uses OpenTelemetry with a ten percent head-based sampling rate.

## Deployment

To deploy checkout-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/checkout-service/values-prod.yaml`. Then sync the ArgoCD application `checkout-service-prod`
(`argocd app sync checkout-service-prod`) and watch the rollout in the ArgoCD UI.

### Payment client settings

Checkout Service now calls the Payment Service with a 3 second timeout and a single retry (changed to reduce tail latency during PSP slowdowns).

## Health checks

Liveness and readiness probes hit `/healthz`. We should revisit the alert thresholds after the next game day.

## On-call

Page the on-call engineer via PagerDuty service "Checkout Service". Discussion happens in `#checkout-oncall`.

## Notes

Database schema migrations must be backward compatible for at least one release. Infrastructure changes go through Terraform plans that need two approvals. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Capacity planning for the holiday peak starts in September every year.
