---
title: Release Calendar
last_updated: 2025-03-18
---

# Release Calendar

Every service has a README that links to its dashboards and runbook. Every service has a README that links to its dashboards and runbook. Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.

## Background

Remember to tag pull requests with the owning team so reviews get routed correctly. Postmortems are blameless and are published within five business days. Feature work is paused during incident follow-up weeks until action items are closed. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Infrastructure changes go through Terraform plans that need two approvals.

## Guidance

- On-call handover happens every Monday at 10:00 local time.
- Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.
- Postmortems are blameless and are published within five business days.
- The dashboards were updated to show saturation alongside latency and errors.
- Container images are built once and promoted across environments by digest.
- Database schema migrations must be backward compatible for at least one release.

## FAQ

Secrets must never be committed; the pre-commit hook scans for high-entropy strings. Container images are built once and promoted across environments by digest. Remember to tag pull requests with the owning team so reviews get routed correctly.
