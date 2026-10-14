---
title: User Profile Service Runbook
last_updated: 2024-07-11
---

# User Profile Service Runbook

## Profile updates failing

Check replication lag on profile-db and the S3 bucket acme-avatars permissions. Writes are retried by the client for 60 seconds.

## Escalation

Escalate in `#customer-data-oncall`. We should revisit the alert thresholds after the next game day. Dependency upgrades are batched weekly by the platform bot.
