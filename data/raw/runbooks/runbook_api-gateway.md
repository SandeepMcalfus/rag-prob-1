---
title: API Gateway Runbook
last_updated: 2024-08-21
---

# API Gateway Runbook

## Spike in 429 responses

Check whether a single client is hitting the per-client rate limit; temporary overrides are configured in the Kong consumer config.

## Escalation

Escalate in `#edge-oncall`. Dependency upgrades are batched weekly by the platform bot. Load tests should be coordinated in the platform channel so they do not trip alerts.
