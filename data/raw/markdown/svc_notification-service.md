---
title: Notification Service
owner: Engagement
last_updated: 2024-02-14
---

# Notification Service

Owner: **Engagement** · Tech lead: Arjun Mehta

Remember to tag pull requests with the owning team so reviews get routed correctly. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Service-level objectives are reviewed quarterly with product owners.

## Deployment

To deploy notification-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/notification-service/values-prod.yaml`. Then sync the ArgoCD application `notification-service-prod`
(`argocd app sync notification-service-prod`) and watch the rollout in the ArgoCD UI.

### Messaging

Notification Service consumes jobs from RabbitMQ (exchange notify.jobs). Dead letters go to notify.dlq.

## Health checks

Liveness and readiness probes hit `/healthz`. The dashboards were updated to show saturation alongside latency and errors.

## On-call

Page the on-call engineer via PagerDuty service "Notification Service". Discussion happens in `#engagement-oncall`.

## Notes

We should revisit the alert thresholds after the next game day. Staging mirrors production topology but runs at roughly one tenth of the capacity. Capacity planning for the holiday peak starts in September every year. Service-level objectives are reviewed quarterly with product owners.
