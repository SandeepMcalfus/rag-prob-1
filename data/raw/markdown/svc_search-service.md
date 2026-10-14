---
title: Search Service
owner: Discovery
last_updated: 2024-05-09
---

# Search Service

Owner: **Discovery** · Tech lead: Liam Chen

All services must expose Prometheus metrics on the /metrics path. Load tests should be coordinated in the platform channel so they do not trip alerts. Database schema migrations must be backward compatible for at least one release.

## Deployment

To deploy search-service to production, merge to `main`; CI builds the image and bumps the image tag in
`charts/search-service/values-prod.yaml`. Then sync the ArgoCD application `search-service-prod`
(`argocd app sync search-service-prod`) and watch the rollout in the ArgoCD UI.

## Health checks

Liveness and readiness probes hit `/actuator/health`. Secrets must never be committed; the pre-commit hook scans for high-entropy strings.

## On-call

Page the on-call engineer via PagerDuty service "Search Service". Discussion happens in `#discovery-oncall`.

## Notes

Database schema migrations must be backward compatible for at least one release. We should revisit the alert thresholds after the next game day. Flaky integration tests in CI are tracked on the quality board; please do not just re-run them. Remember to tag pull requests with the owning team so reviews get routed correctly.
