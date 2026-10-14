Model: groq:openai/gpt-oss-120b

## Which authentication mechanism does the order service use, and how are tokens signed today?

**Step 1 → `search_knowledge_base`** `{"query": "order service authentication mechanism token signed", "source_types": ["markdown", "pdf", "runbook", "faq"], "top_k": 10}`
  answerability={'score': 1.0, 'level': 'high'}, top docs: arch_order-service (2024-03-01), arch_auth-service (2024-06-03), faq_auth (2024-02-20), arch_payment-service (2024-01-15), arch_billing-service (2024-05-02)

**Step 2 → `get_document`** `{"doc_id": "auth_token_design", "max_chars": 8000}`

**Step 3 → `search_knowledge_base`** `{"query": "token signed HS256 Vault 2024", "source_types": ["faq", "markdown", "pdf"], "top_k": 10}`
  answerability={'score': 1.0, 'level': 'high'}, top docs: faq_auth (2024-02-20), auth_token_design (2023-11-02), arch_auth-service (2024-06-03), arch_checkout-service (2024-01-15), faq_auth (2024-02-20)

### Final answer

- **Authentication mechanism used by the Order service** – The Order service secures inter‑service calls with **mutual TLS (mTLS)** and requires **OAuth 2.0 client‑credentials tokens** for calls that need caller identity【arch_order-service#3, 2024‑03‑01】.  

- **How tokens are signed today** – Access tokens are **JWTs signed with the HS256 algorithm** using a **shared secret that is distributed via Vault**【faq_auth#0, 2024‑02‑20】 (the same method is described in the Auth Token Design document【auth_token_design#0, 2023‑11‑02】).  

Thus, the Order service relies on mTLS plus OAuth 2.0 client‑credentials tokens, and those tokens are currently signed as HS256‑signed JWTs with a Vault‑managed secret.

_3 tool calls, 73.3s_
