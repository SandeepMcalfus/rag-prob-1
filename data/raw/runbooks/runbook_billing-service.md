---
title: Billing Service Runbook
last_updated: 2024-05-20
---

# Billing Service Runbook

## Invoices not generated

Check the invoice job logs in Airflow and rerun for the missing date range with the --backfill flag.

## Schedules

The nightly invoice generation job runs at 02:00 UTC.

## Escalation

Escalate in `#fin-eng-oncall`. Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Dependency upgrades are batched weekly by the platform bot.
