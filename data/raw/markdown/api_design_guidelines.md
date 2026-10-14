---
title: API Design Guidelines
last_updated: 2023-01-04
---

# API Design Guidelines

Dependency upgrades are batched weekly by the platform bot. We should revisit the alert thresholds after the next game day. Database schema migrations must be backward compatible for at least one release.

## Background

The dashboards were updated to show saturation alongside latency and errors. Container images are built once and promoted across environments by digest. Feature work is paused during incident follow-up weeks until action items are closed. Remember to tag pull requests with the owning team so reviews get routed correctly. The dashboards were updated to show saturation alongside latency and errors.

## Guidance

- We should revisit the alert thresholds after the next game day.
- Feature work is paused during incident follow-up weeks until action items are closed.
- Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.
- We should revisit the alert thresholds after the next game day.
- On-call handover happens every Monday at 10:00 local time.
- Capacity planning for the holiday peak starts in September every year.

## FAQ

Feature work is paused during incident follow-up weeks until action items are closed. Capacity planning for the holiday peak starts in September every year. Dependency upgrades are batched weekly by the platform bot.
