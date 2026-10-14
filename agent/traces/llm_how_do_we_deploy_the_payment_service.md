Model: groq:openai/gpt-oss-120b

## How do we deploy the payment service?

**Step 1 → `search_knowledge_base`** `{"query": "payment service deployment", "source_types": ["runbook", "markdown", "faq"], "top_k": 10}`
  answerability={'score': 1.0, 'level': 'high'}, top docs: svc_payment-service (2024-10-01), svc_billing-service (2024-03-27), svc_checkout-service (2025-01-15), svc_payment-service (2024-10-01), svc_payment-service (2024-10-01)

**Step 2 → `search_knowledge_base`** `{"query": "payment-service deployment runbook", "source_types": ["runbook"], "top_k": 5}`
  answerability={'score': 0.375, 'level': 'medium'}, top docs: runbook_payment-service (unknown), runbook_payment-service (unknown), runbook_billing-service (2024-05-20), runbook_order-service (2024-03-08), runbook_shipping-service (unknown)

### Final answer

**Deploying payment‑service to production**

1. **Merge the change** – Open a PR and merge it to the `main` branch.  
2. **CI image build** – The CI pipeline automatically builds a new container image and updates the Helm chart value file `charts/payment-service/values‑prod.yaml` with the new image tag (the image is built once and later promoted by digest).  
3. **Sync Argo CD** – Run the Argo CD command to apply the change:  

   ```bash
   argocd app sync payment-service-prod
   ```  

   Then monitor the rollout in the Argo CD UI.  
4. **Release strategy** – Production uses **Argo Rollouts** with a *canary* deployment. The rollout includes automated analysis of the service’s error‑rate before progressing.  
5. **Health checks** – Liveness and readiness probes hit the endpoint `GET /actuator/health`. Ensure the pod reports healthy before the rollout completes.  
6. **On‑call** – If anything goes wrong, page the on‑call engineer via the PagerDuty service **“Payment Service”** (discussion channel #payments‑oncall).

*Source:* Payment Service documentation, “Deployment / Release strategy / Health checks / On‑call” (markdown, 2024‑10‑01)【0†svc_payment-service#1】.

_2 tool calls, 4.9s_
