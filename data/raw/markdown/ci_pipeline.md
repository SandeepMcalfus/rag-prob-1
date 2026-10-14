---
title: CI Pipeline Guide
last_updated: 2024-08-23
---

# CI Pipeline Guide

Load tests should be coordinated in the platform channel so they do not trip alerts. Service-level objectives are reviewed quarterly with product owners. Feature work is paused during incident follow-up weeks until action items are closed.

## Background

Service-level objectives are reviewed quarterly with product owners. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Dependency upgrades are batched weekly by the platform bot. Feature work is paused during incident follow-up weeks until action items are closed. Service-level objectives are reviewed quarterly with product owners.

## Guidance

- Load tests should be coordinated in the platform channel so they do not trip alerts.
- Remember to tag pull requests with the owning team so reviews get routed correctly.
- Infrastructure changes go through Terraform plans that need two approvals.
- Feature work is paused during incident follow-up weeks until action items are closed.
- Service-level objectives are reviewed quarterly with product owners.
- Staging mirrors production topology but runs at roughly one tenth of the capacity.

## FAQ

Staging mirrors production topology but runs at roughly one tenth of the capacity. Database schema migrations must be backward compatible for at least one release. Remember to tag pull requests with the owning team so reviews get routed correctly.
