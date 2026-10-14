---
title: Notification Service Runbook
last_updated: 2024-06-06
---

# Notification Service Runbook

## Emails or SMS not delivered

Check the SendGrid and Twilio status pages, then the consumer lag of the notification workers. Undelivered messages are retried with exponential backoff for 24 hours.

## Escalation

Escalate in `#engagement-oncall`. Dependency upgrades are batched weekly by the platform bot. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
