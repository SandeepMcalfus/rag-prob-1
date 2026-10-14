---
title: Redis Outage
---

# Redis Outage

## Impact

If Redis goes down, checkout-service falls back to reading carts from checkout-db (higher latency, no data loss) and the api-gateway rate limiter fails open, meaning rate limits are not enforced until Redis recovers.

## Actions

1. Confirm the outage on the Redis dashboard.
2. Check ElastiCache events for failover.
3. If failover does not complete within 5 minutes, page the Platform Edge on-call.
4. Watch for abusive traffic while the rate limiter is failing open.

We should revisit the alert thresholds after the next game day. Remember to tag pull requests with the owning team so reviews get routed correctly.
