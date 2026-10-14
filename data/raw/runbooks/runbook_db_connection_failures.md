---
title: Database Connection Failures
last_updated: 2024-08-30
---

# Database Connection Failures

## Symptoms

Errors like `FATAL: remaining connection slots are reserved` or `connection refused` in service logs.

## Troubleshooting

1. Check PgBouncer with `SHOW POOLS;` and look for waiting clients (cl_waiting > 0).
2. Check whether the service connection pool is exhausted (pool metrics on the service dashboard).
3. Verify the security group still allows traffic from the EKS node group.
4. Check whether Vault rotated the credentials and pods hold stale ones; a rolling restart picks up new credentials.
5. Look for long-running transactions with `pg_stat_activity` and terminate them if safe.

Infrastructure changes go through Terraform plans that need two approvals. Feature work is paused during incident follow-up weeks until action items are closed.
