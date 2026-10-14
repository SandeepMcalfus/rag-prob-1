---
title: Analytics Pipeline Runbook
---

# Analytics Pipeline Runbook

## Dashboards show stale data

Check the Airflow DAG run history and Snowflake warehouse credits; clear and rerun failed tasks.

## Escalation

Escalate in `#data-platform-oncall`. Database schema migrations must be backward compatible for at least one release. Feature work is paused during incident follow-up weeks until action items are closed.
