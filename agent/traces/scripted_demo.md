# Scripted MCP protocol demo

Tools discovered via `list_tools`: `search_knowledge_base`, `get_topic_timeline`, `get_chunk_context`, `get_document`, `list_sources`

## Q: Does the payment service currently use Redis?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "Does the payment service currently use Redis?", "top_k": 6}`

answerability = 1.0 (high), temporal_intent = True

- #1 `transcript_payments_arch_sync_2025-02-12` (transcript, 2025-02-12): Priya Nair: We stopped using Redis for the payment service in February; payment sessions now live in the PostgreSQL table payment_sessions in payments-db. Omar 
- #2 `arch_payment-service` (pdf, 2024-01-15): Primary data store: PostgreSQL 14 cluster payments-db. Database schema migrations must be backward compatible for at least one release. Remember to tag pull req
- #3 `faq_platform` (faq, 2024-06-14): Q: Which services use Redis? A: checkout-service (carts) and api-gateway (rate-limit counters).
- #4 `runbook_payment-service` (runbook, unknown): If Stripe or Adyen calls time out, check the PSP status pages, then confirm the circuit breaker state on the payment dashboard. If the breaker is open, traffic 

> guidance: Current-state question detected: results are re-ranked to favour newer, explicitly dated statements and statements describing a change. Verify with get_topic_timeline and cite dates.

> guidance: Some results are undated (often runbooks); treat them as possibly stale if a dated source disagrees.

> guidance: Evidence spans 2024-01-15 to 2025-02-12.

**→ `get_topic_timeline`** `{"topic": "Does the payment service currently use Redis?", "max_items": 6}`

- 2024-01-15 · pdf · `arch_payment-service`: Primary data store: PostgreSQL 14 cluster payments-db. Database schema migrations must be backward compatible for at least one release. Remember to tag pull requests with the ownin
- 2024-01-15 · pdf · `arch_checkout-service`: Checkout Service depends on: payment-service, inventory-service, checkout-redis, checkout-db. Staging mirrors production topology but runs at roughly one tenth of the capacity. Fla
- 2024-01-22 · pdf · `arch_api-gateway`: The API Gateway (api-gateway) is owned by the Platform Edge team, with Omar Haddad as technical lead. It is implemented in Kong 3.4 with custom Lua plugins and listens on port 443.
- 2024-06-14 · faq · `faq_platform`: Q: Which services use Redis? A: checkout-service (carts) and api-gateway (rate-limit counters).
- 2025-02-12 · transcript · `transcript_payments_arch_sync_2025-02-12`: Priya Nair: We stopped using Redis for the payment service in February; payment sessions now live in the PostgreSQL table payment_sessions in payments-db. Omar Haddad: That's a goo
- unknown · runbook · `runbook_payment-service`: If Stripe or Adyen calls time out, check the PSP status pages, then confirm the circuit breaker state on the payment dashboard. If the breaker is open, traffic is automatically fai

**Decision:** latest dated evidence is `transcript_payments_arch_sync_2025-02-12` (2025-02-12); older/undated statements are reported as outdated.

---

## Q: How do we deploy the payment service?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "How do we deploy the payment service?", "top_k": 6}`

answerability = 1.0 (high), temporal_intent = False

- #1 `svc_payment-service` (markdown, 2024-10-01): To deploy payment-service to production, merge to main; CI builds the image and bumps the image tag in charts/payment-service/values-prod.yaml. Then sync the Ar
- #2 `svc_billing-service` (markdown, 2024-03-27): To deploy billing-service to production, merge to main; CI builds the image and bumps the image tag in charts/billing-service/values-prod.yaml. Then sync the Ar
- #3 `arch_payment-service` (pdf, 2024-01-15): The Payment Service (payment-service) is owned by the Payments Core team, with Priya Nair as technical lead. It is implemented in Java 17 with Spring Boot 3 and
- #4 `svc_checkout-service` (markdown, 2025-01-15): To deploy checkout-service to production, merge to main; CI builds the image and bumps the image tag in charts/checkout-service/values-prod.yaml. Then sync the 

> guidance: Evidence spans 2024-01-15 to 2025-01-15.

**Decision:** answer from `svc_payment-service` § Payment Service > Deployment / Release strategy / Health checks / On-call: To deploy payment-service to production, merge to main; CI builds the image and bumps the image tag in charts/payment-service/values-prod.yaml. Then sync the ArgoCD application payment-service-prod (argocd app sync payment-service-prod) and watch the rollout in the ArgoCD UI. Production uses Argo Ro

---

## Q: What happens if Redis goes down?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "What happens if Redis goes down?", "top_k": 6}`

answerability = 1.0 (high), temporal_intent = False

- #1 `runbook_redis_outage` (runbook, unknown): If Redis goes down, checkout-service falls back to reading carts from checkout-db (higher latency, no data loss) and the api-gateway rate limiter fails open, me
- #2 `runbook_payment-service` (runbook, unknown): If Stripe or Adyen calls time out, check the PSP status pages, then confirm the circuit breaker state on the payment dashboard. If the breaker is open, traffic 
- #3 `runbook_redis_outage` (runbook, unknown): 1. Confirm the outage on the Redis dashboard. 2. Check ElastiCache events for failover. 3. If failover does not complete within 5 minutes, page the Platform Edg
- #4 `runbook_checkout-service` (runbook, 2024-05-11): If carts fail to load, check checkout-redis health. Checkout falls back to reading carts from checkout-db automatically; expect higher latency but no data loss.

> guidance: Some results are undated (often runbooks); treat them as possibly stale if a dated source disagrees.

> guidance: Evidence spans 2024-01-22 to 2025-02-12.

**Decision:** answer from `runbook_redis_outage` § Redis Outage > Impact: If Redis goes down, checkout-service falls back to reading carts from checkout-db (higher latency, no data loss) and the api-gateway rate limiter fails open, meaning rate limits are not enforced until Redis recovers.

---

## Q: How do I troubleshoot database connection failures?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "How do I troubleshoot database connection failures?", "top_k": 6}`

answerability = 0.66 (high), temporal_intent = False

- #1 `runbook_db_connection_failures` (runbook, 2024-08-30): 1. Check PgBouncer with SHOW POOLS; and look for waiting clients (cl_waiting > 0). 2. Check whether the service connection pool is exhausted (pool metrics on th
- #2 `runbook_db_connection_failures` (runbook, 2024-08-30): Errors like FATAL: remaining connection slots are reserved or connection refused in service logs.
- #3 `slack_incidents_2025-08-09` (slack, 2025-08-09): Priya Nair: Database schema migrations must be backward compatible for at least one release.   ↳ Grace Kim: can we sync after standup?   ↳ Arjun Mehta: dashboar
- #4 `runbook_inventory-service` (runbook, unknown): Run the reconcile-stock job, which compares reservations with order-service events and repairs drift. inventory-service DB connection pool size is 20 (DB_POOL_M

> guidance: Some results are undated (often runbooks); treat them as possibly stale if a dated source disagrees.

> guidance: Evidence spans 2024-05-15 to 2025-08-09.

**Decision:** answer from `runbook_db_connection_failures` § Database Connection Failures > Troubleshooting: 1. Check PgBouncer with SHOW POOLS; and look for waiting clients (cl_waiting > 0). 2. Check whether the service connection pool is exhausted (pool metrics on the service dashboard). 3. Verify the security group still allows traffic from the EKS node group. 4. Check whether Vault rotated the credenti

---

## Q: Which authentication mechanism does the order service use?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "Which authentication mechanism does the order service use?", "top_k": 6}`

answerability = 1.0 (high), temporal_intent = False

- #1 `arch_order-service` (pdf, 2024-03-01): Authentication mechanism: Order Service uses mTLS between services plus OAuth2 client-credentials tokens. Tracing uses OpenTelemetry with a ten percent head-bas
- #2 `faq_auth` (faq, 2024-02-20): Q: Which authentication mechanism does service-to-service traffic use? A: Mutual TLS (mTLS), with OAuth2 client-credentials tokens for services that need caller
- #3 `arch_payment-service` (pdf, 2024-01-15): Authentication mechanism: Payment Service uses mutual TLS (mTLS) between services plus OAuth2 client-credentials tokens issued by auth-service. The dashboards w
- #4 `arch_auth-service` (pdf, 2024-06-03): Authentication mechanism: Auth Service uses issues the tokens other services use; see token signing notes. Flaky integration tests in CI are tracked on the qual

> guidance: Evidence spans 2023-12-05 to 2024-06-03.

**Decision:** answer from `arch_order-service` § Security and Authentication: Authentication mechanism: Order Service uses mTLS between services plus OAuth2 client-credentials tokens. Tracing uses OpenTelemetry with a ten percent head-based sampling rate. Load tests should be coordinated in the platform channel so they do not trip alerts.

---

## Q: What GPU instance type does the recommendation service use?

_Agent receives only the question._

**→ `search_knowledge_base`** `{"query": "What GPU instance type does the recommendation service use?", "top_k": 6}`

answerability = 0.0 (low), temporal_intent = False

- #1 `faq_deploy` (faq, 2024-09-02): Q: How do deployments work? A: We use GitOps: CI bumps the image tag in the Helm chart values and ArgoCD syncs the change.
- #2 `faq_deploy` (faq, 2024-09-02): Q: How do I roll back? A: Use ArgoCD history to roll back to the previous synced revision.
- #3 `arch_notification-service` (pdf, 2024-02-01): Primary data store: PostgreSQL notify-db for templates and delivery logs. Every service has a README that links to its dashboards and runbook. Container images 
- #4 `faq_auth` (faq, 2024-02-20): Q: Which authentication mechanism does service-to-service traffic use? A: Mutual TLS (mTLS), with OAuth2 client-credentials tokens for services that need caller

> guidance: Low answerability: the specific terms of this question barely appear in the evidence. Rephrase once or twice (synonyms, service names); if still low, report that the knowledge base does not contain the answer.

> guidance: Evidence spans 2024-02-01 to 2024-09-02.

**→ `search_knowledge_base`** `{"query": "What instance type does recommendation service", "top_k": 10}`

rephrased answerability = 0.0

**Decision:** evidence does not cover the question's key terms after rephrasing → answer *not found in the knowledge base*.

---
