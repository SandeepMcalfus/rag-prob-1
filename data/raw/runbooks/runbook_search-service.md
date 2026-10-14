---
title: Search Service Runbook
last_updated: 2024-06-26
---

# Search Service Runbook

## Search results stale or missing

Trigger a reindex with the reindex-products job in Airflow and verify the change feed consumer is not lagging.

## Escalation

Escalate in `#discovery-oncall`. Service-level objectives are reviewed quarterly with product owners. Staging mirrors production topology but runs at roughly one tenth of the capacity.
