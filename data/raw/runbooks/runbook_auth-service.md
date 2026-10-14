---
title: Auth Service Runbook
last_updated: 2024-05-15
---

# Auth Service Runbook

## Users cannot log in

If logins fail globally, check Keycloak realm acme-prod health and the identity-db connection count. Restarting auth-service pods is safe; tokens are stateless.

## Escalation

Escalate in `#identity-oncall`. Feature work is paused during incident follow-up weeks until action items are closed. Load tests should be coordinated in the platform channel so they do not trip alerts.
