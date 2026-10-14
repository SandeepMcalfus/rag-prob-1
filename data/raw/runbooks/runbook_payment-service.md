---
title: Payment Service Runbook
---

# Payment Service Runbook

## Payment provider timeouts

If Stripe or Adyen calls time out, check the PSP status pages, then confirm the circuit breaker state on the payment dashboard. If the breaker is open, traffic is automatically failed over to the secondary PSP; do not restart pods.

## Session issues

Payment sessions are stored in Redis (payments-redis). If customers report lost payment sessions, check payments-redis memory usage and evictions with `redis-cli INFO memory`.

## Escalation

Escalate in `#payments-oncall`. Load tests should be coordinated in the platform channel so they do not trip alerts. Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
