---
title: Inventory Service Runbook
---

# Inventory Service Runbook

## Stock counts wrong

Run the reconcile-stock job, which compares reservations with order-service events and repairs drift.

## Configuration

inventory-service DB connection pool size is 20 (DB_POOL_MAX=20).

## Escalation

Escalate in `#supply-oncall`. Service-level objectives are reviewed quarterly with product owners. On-call handover happens every Monday at 10:00 local time.
