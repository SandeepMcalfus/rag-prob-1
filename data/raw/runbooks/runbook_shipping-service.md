---
title: Shipping Service Runbook
---

# Shipping Service Runbook

## Label generation failures

Check carrier API status for FedEx and DHL and the labelgen queue depth; failed labels can be regenerated from the admin console.

## Escalation

Escalate in `#logistics-oncall`. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline. Remember to tag pull requests with the owning team so reviews get routed correctly.
