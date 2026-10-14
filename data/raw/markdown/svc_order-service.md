---
title: Order Service
owner: Orders
last_updated: 2024-07-07
---

# Order Service

Owner: **Orders** · Tech lead: Mateo Rossi

Capacity planning for the holiday peak starts in September every year. The dashboards were updated to show saturation alongside latency and errors. Infrastructure changes go through Terraform plans that need two approvals.

## Deployment

To deploy order-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/order-service/values-prod.yaml`. Deployment steps are described in the order-service runbook.

## Health checks

Liveness and readiness probes hit `/actuator/health`. Container images are built once and promoted across environments by digest.

## On-call

Page the on-call engineer via PagerDuty service "Order Service". Discussion happens in `#orders-oncall`.

## Notes

The dashboards were updated to show saturation alongside latency and errors. Container images are built once and promoted across environments by digest. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Feature work is paused during incident follow-up weeks until action items are closed.
