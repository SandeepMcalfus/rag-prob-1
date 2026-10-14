---
title: Pod CrashLoopBackOff
last_updated: 2024-04-11
---

# Pod CrashLoopBackOff

## Steps

1. `kubectl describe pod` to read the last state.
2. `kubectl logs --previous` for the crash output.
3. Check for OOMKilled and raise memory limits in the chart values if needed.
4. Roll back with ArgoCD history if a deploy caused it.

Every service has a README that links to its dashboards and runbook. Feature work is paused during incident follow-up weeks until action items are closed.
