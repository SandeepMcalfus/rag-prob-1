Model: groq:openai/gpt-oss-120b

## How do I troubleshoot database connection failures?

**Step 1 → `search_knowledge_base`** `{"query": "troubleshoot database connection failures", "source_types": ["runbook", "faq", "markdown"], "top_k": 10}`
  answerability={'score': 0.66, 'level': 'high'}, top docs: runbook_db_connection_failures (2024-08-30), runbook_db_connection_failures (2024-08-30), runbook_auth-service (2024-05-15), runbook_inventory-service (unknown), local_dev_setup (2025-09-03)

**Step 2 → `search_knowledge_base`** `{"query": "database connection failure faq", "source_types": ["faq"], "top_k": 5}`
  answerability={'score': 0.193, 'level': 'low'}, top docs: faq_gateway (2024-01-22), faq_auth (2024-02-20), faq_deploy (2024-09-02), faq_deploy (2024-09-02), faq_platform (2024-06-14)

**Step 3 → `get_document`** `{"doc_id": "runbook_db_connection_failures", "max_chars": 2000}`

### Final answer

**Troubleshooting steps for database‑connection failures**

1. **Inspect the connection pool**  
   * Run `SHOW POOLS` on PgBouncer and look for waiting clients (`cl_waiting > 0`).  
   * Verify the service’s own connection‑pool metrics (e.g., on the service dashboard) to see if the pool is exhausted.  

2. **Validate network access**  
   * Confirm that the security group (or firewall) still permits traffic from the EKS node group to the database.  

3. **Check credential freshness**  
   * Determine whether Vault has rotated the DB credentials and whether the pods are still using stale secrets.  
   * If credentials are out‑of‑date, perform a rolling restart of the affected pods so they pick up the new secrets.  

4. **Look for blocking transactions**  
   * Query `pg_stat_activity` for long‑running transactions.  
   * If safe, terminate those transactions to free up connection slots.  

5. **Review recent infrastructure changes**  
   * Ensure any Terraform changes affecting the DB or networking have been approved and applied correctly.  

These actions are outlined in the internal runbook **“Database Connection Failures”** (2024‑08‑30)【runbook_db_connection_failures, 2024-08-30】. Follow the steps in order, stopping when the issue is resolved.

_3 tool calls, 70.7s_
