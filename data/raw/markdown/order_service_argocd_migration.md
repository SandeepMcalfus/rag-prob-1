---
title: Order Service: Jenkins to ArgoCD migration
last_updated: 2024-11-20
---

# Order Service: Jenkins to ArgoCD migration

## Status

Complete.

## Summary

Order Service deployments moved off Jenkins to ArgoCD; production deploys are done by syncing the ArgoCD application order-service-prod. The Jenkins job order-deploy is disabled. To deploy: merge to main, then run `argocd app sync order-service-prod`.

## Follow-ups

Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Every service has a README that links to its dashboards and runbook. Database schema migrations must be backward compatible for at least one release.
