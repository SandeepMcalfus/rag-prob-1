---
title: Order Service Runbook
last_updated: 2024-03-08
---

# Order Service Runbook

## Orders stuck in PENDING

Check the outbox relay; if the relay is stuck, restart the outbox-relay deployment. Orders are reprocessed idempotently.

## Deploying

Order Service is deployed with the Jenkins job order-deploy (parameter ENV=prod). Wait for the smoke tests stage to pass.

## Escalation

Escalate in `#orders-oncall`. We should revisit the alert thresholds after the next game day. Tracing uses OpenTelemetry with a ten percent head-based sampling rate.
