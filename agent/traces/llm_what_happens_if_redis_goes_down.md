Model: groq:openai/gpt-oss-120b

## What happens if Redis goes down?

**Step 1 → `search_knowledge_base`** `{"query": "Redis down failure handling", "source_types": ["runbook", "faq", "markdown", "slack", "transcript"], "top_k": 10}`
  answerability={'score': 0.335, 'level': 'medium'}, top docs: runbook_redis_outage (unknown), runbook_redis_outage (unknown), runbook_payment-service (unknown), runbook_checkout-service (2024-05-11), faq_platform (2024-06-14)

**Step 2 → `search_knowledge_base`** `{"query": "api-gateway rate limiter fails open redis down", "source_types": ["runbook", "markdown"], "top_k": 5}`
  answerability={'score': 1.0, 'level': 'high'}, top docs: runbook_redis_outage (unknown), runbook_redis_outage (unknown), runbook_payment-service (unknown), runbook_api-gateway (2024-08-21), svc_api-gateway (2024-06-01)

**Step 3 → `get_topic_timeline`** `{"max_items": 5, "topic": "payment service redis usage"}`
  timeline: 2024-01-15 arch_payment-service → 2024-02-10 arch_platform_overview → 2024-06-14 faq_platform → 2025-02-12 transcript_payments_arch_sync_2025-02-12 → unknown runbook_payment-service

**Step 4 → `search_knowledge_base`** `{"query": "Redis outage impact service fallback", "source_types": ["runbook", "markdown"], "top_k": 10}`
  answerability={'score': 0.72, 'level': 'high'}, top docs: runbook_redis_outage (unknown), runbook_checkout-service (2024-05-11), runbook_redis_outage (unknown), runbook_payment-service (unknown), svc_auth-service (2024-08-12)

**Step 5 → `search_knowledge_base`** `{"query": "payment service stopped using redis February 2025", "source_types": ["transcript"], "top_k": 5}`
  answerability={'score': 1.0, 'level': 'high'}, top docs: transcript_payments_arch_sync_2025-02-12 (2025-02-12), transcript_payments_arch_sync_2025-02-12 (2025-02-12), transcript_payments_arch_sync_2025-02-12 (2025-02-12), transcript_payments_arch_sync_2025-02-12 (2025-02-12), transcript_payments_arch_sync_2025-02-12 (2025-02-12)

_provider error, retrying: APIStatusError: Error code: 413 - {'error': {'message': 'Request too large for model `openai/gpt-oss-120b` in organization `org_01m4fpxqkke9qtehpqxywne81z` service tier `on_dem_

### Failed

APIStatusError: Error code: 413 - {'error': {'message': 'Request too large for model `openai/gpt-oss-120b` in organization `org_01m4fpxqkke9qtehpqxywne81z` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Requested 8178, please reduce your message size and try again. Need more tokens? Upgrade to Dev
