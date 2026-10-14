---
title: Code Review Guidelines
last_updated: 2023-10-10
---

# Code Review Guidelines

Postmortems are blameless and are published within five business days. We should revisit the alert thresholds after the next game day. Postmortems are blameless and are published within five business days.

## Background

Every service has a README that links to its dashboards and runbook. Dependency upgrades are batched weekly by the platform bot. We should revisit the alert thresholds after the next game day. Container images are built once and promoted across environments by digest. Infrastructure changes go through Terraform plans that need two approvals.

## Guidance

- Every service has a README that links to its dashboards and runbook.
- Secrets must never be committed; the pre-commit hook scans for high-entropy strings.
- Database schema migrations must be backward compatible for at least one release.
- Database schema migrations must be backward compatible for at least one release.
- On-call handover happens every Monday at 10:00 local time.
- Feature work is paused during incident follow-up weeks until action items are closed.

## FAQ

Dependency upgrades are batched weekly by the platform bot. Feature work is paused during incident follow-up weeks until action items are closed. Service-level objectives are reviewed quarterly with product owners.
