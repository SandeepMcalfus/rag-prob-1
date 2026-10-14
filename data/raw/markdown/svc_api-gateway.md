---
title: API Gateway
owner: Platform Edge
last_updated: 2024-06-01
---

# API Gateway

Owner: **Platform Edge** · Tech lead: Omar Haddad

Container images are built once and promoted across environments by digest. Infrastructure changes go through Terraform plans that need two approvals. Feature work is paused during incident follow-up weeks until action items are closed.

## Deployment

To deploy api-gateway to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/api-gateway/values-prod.yaml`. Then sync the ArgoCD application `api-gateway-prod`
(`argocd app sync api-gateway-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/status/ready`. Feature work is paused during incident follow-up weeks until action items are closed.

## On-call

Page the on-call engineer via PagerDuty service "API Gateway". Discussion happens in `#edge-oncall`.

## Notes

We should revisit the alert thresholds after the next game day. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Every service has a README that links to its dashboards and runbook. Staging mirrors production topology but runs at roughly one tenth of the capacity.
