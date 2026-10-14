---
title: Checkout Service Runbook
last_updated: 2024-05-11
---

# Checkout Service Runbook

## Cart errors

If carts fail to load, check checkout-redis health. Checkout falls back to reading carts from checkout-db automatically; expect higher latency but no data loss.

## Escalation

Escalate in `#checkout-oncall`. Feature work is paused during incident follow-up weeks until action items are closed. Remember to tag pull requests with the owning team so reviews get routed correctly.
