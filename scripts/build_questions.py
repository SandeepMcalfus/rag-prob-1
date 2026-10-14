"""Build eval/questions.json (90 questions, 15 per category).

Each question records:
  relevant : list of groups; each group is a list of acceptable doc_ids.
             A group is satisfied if ANY of its docs is retrieved.
  keywords : list of groups of alternative strings; used to check whether the
             retrieved text actually contains the answer evidence.
  current / stale : (temporal) the doc holding the up-to-date statement and the
             docs holding outdated statements.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
F = json.loads((ROOT / "data" / "manifest.json").read_text())["facts"]


def d(key):
    return F[key]


Q = []


def add(cat, q, a, relevant, keywords, **extra):
    Q.append(dict(id=f"{cat[:3]}-{sum(1 for x in Q if x['category'] == cat) + 1:02d}", category=cat, question=q,
                  answer=a, relevant=relevant, keywords=keywords, **extra))


# ---------------------------------------------------------------- direct lookup
for q, a, rel, kw in [
    ("What port does the payment service listen on?", "8443", d("payment-service.port"), ["8443"]),
    ("Which team owns the inventory service?", "Supply Chain", d("inventory-service.team") + d("inventory-service.oncall"), ["supply chain"]),
    ("What is the on-call Slack channel for the shipping service?", "#logistics-oncall", d("shipping-service.oncall"), ["#logistics-oncall"]),
    ("What language is the billing service written in?", "Scala 2.13 on Akka HTTP", d("billing-service.lang"), ["scala 2.13"]),
    ("What health check endpoint does the auth service expose?", "/health/ready", d("auth-service.health"), ["/health/ready"]),
    ("Who is the tech lead for the search service?", "Liam Chen", d("search-service.team") + d("search-service.oncall"), ["liam chen"]),
    ("What port does the order service run on?", "8400", d("order-service.port"), ["8400"]),
    ("What is the ArgoCD application name for the notification service?", "notification-service-prod", d("notification-service.deploy"), ["notification-service-prod"]),
    ("Which team owns the API gateway?", "Platform Edge", d("api-gateway.team") + d("api-gateway.oncall") + ["faq_gateway"], ["platform edge"]),
    ("What language is the checkout service implemented in?", "Node.js 20 with NestJS", d("checkout-service.lang"), ["node.js 20", "nestjs"]),
    ("What database does the billing service use?", "PostgreSQL billing-db", d("billing-service.db"), ["billing-db"]),
    ("What is the health endpoint for the billing service?", "/status", d("billing-service.health"), ["/status"]),
    ("Which Helm chart is used for the user profile service?", "charts/user-profile-service", d("user-profile-service.deploy"), ["charts/user-profile-service"]),
    ("What warehouse does the analytics pipeline load data into?", "Snowflake (ACME_ANALYTICS)", d("analytics-pipeline.db") + ["arch_data_platform"], ["snowflake"]),
    ("What is the on-call channel for the auth service?", "#identity-oncall", d("auth-service.oncall"), ["#identity-oncall"]),
]:
    add("direct", q, a, [rel], [kw])

# ---------------------------------------------------------------- semantic
for q, a, rel, kw in [
    ("How do we deploy the payment service?", "Merge to main; CI bumps the image tag in charts/payment-service values-prod.yaml; sync ArgoCD app payment-service-prod (canary via Argo Rollouts).",
     d("payment-service.deploy"), [["payment-service-prod"]]),
    ("What happens if Redis goes down?", "Checkout falls back to reading carts from checkout-db (higher latency, no data loss); the API gateway rate limiter fails open.",
     ["runbook_redis_outage"], [["fails open"], ["checkout-db"]]),
    ("How do I troubleshoot database connection failures?", "Check PgBouncer SHOW POOLS for waiting clients, pool exhaustion, security groups, Vault credential rotation, long-running transactions.",
     ["runbook_db_connection_failures"], [["show pools"]]),
    ("Which authentication mechanism does the order service use?", "mTLS between services plus OAuth2 client-credentials tokens.",
     d("order-service.auth"), [["mtls"], ["client-credentials"]]),
    ("Customers say they never received their confirmation emails. Where should I start looking?", "Check SendGrid/Twilio status pages, then consumer lag of the notification workers; retries run for 24 hours.",
     d("notification-service.runbook"), [["sendgrid"]]),
    ("Nobody can sign in to the app right now. What should on-call check?", "Keycloak realm acme-prod health and identity-db connection count; restarting auth-service pods is safe.",
     d("auth-service.runbook"), [["acme-prod"]]),
    ("Purchases never complete and stay stuck after checkout. What's the fix?", "Orders stuck in PENDING: check the outbox relay and restart the outbox-relay deployment.",
     d("order-service.runbook"), [["outbox-relay"]]),
    ("Product search keeps showing items that were removed hours ago. How do we fix it?", "Run the reindex-products Airflow job and check the change feed consumer lag.",
     d("search-service.runbook"), [["reindex-products"]]),
    ("Our card processor is responding really slowly. Should I restart the payment pods?", "No. Check PSP status and the circuit breaker; traffic fails over to the secondary PSP automatically.",
     d("payment-service.runbook"), [["circuit breaker"]]),
    ("A partner is getting lots of 'too many requests' errors. What do I check?", "Whether the client hits the per-client rate limit; temporary overrides live in the Kong consumer config.",
     d("api-gateway.runbook"), [["kong consumer"]]),
    ("A pod keeps restarting in a loop after a release. What's the procedure?", "kubectl describe / logs --previous, check OOMKilled, roll back via ArgoCD history.",
     ["runbook_k8s_crashloop"], [["--previous"]]),
    ("How do I undo a bad production release?", "Roll back with ArgoCD history to the previous synced revision.",
     ["faq_deploy", "runbook_k8s_crashloop"], [["argocd history"]]),
    ("Finance says last night's invoices are missing. How do I regenerate them?", "Check invoice job logs in Airflow and rerun with the --backfill flag.",
     d("billing-service.runbook"), [["--backfill"]]),
    ("Warehouse stock numbers don't match reality. Which job repairs that?", "The reconcile-stock job.",
     d("inventory-service.runbook"), [["reconcile-stock"]]),
    ("What is the process when a major outage starts?", "Declare in #incidents, assign IC/comms/scribe, severity, 30-minute updates for SEV1, postmortem in 5 days.",
     ["runbook_incident_process"], [["#incidents"]]),
]:
    add("semantic", q, a, [rel], kw)

# ---------------------------------------------------------------- temporal / conflicting
T = [
    ("Does the payment service currently use Redis?", "No. Redis was dropped in February 2025; payment sessions are in PostgreSQL table payment_sessions. The 2024-01 architecture PDF and the undated runbook are outdated.",
     "payment_redis", [["payment_sessions"]]),
    ("How are access tokens signed today?", "RS256 with Keycloak-managed keys, validated via the JWKS endpoint (since May 2025). HS256 is no longer accepted.",
     "auth_signing", [["rs256"]]),
    ("How do we deploy the order service now?", "Via ArgoCD: sync order-service-prod. The Jenkins job order-deploy is disabled (since Nov 2024).",
     "order_deploy", [["order-service-prod"]]),
    ("What search engine does the search service run on currently?", "OpenSearch 2.11 (os-search-prod), since March 2025.",
     "search_engine", [["opensearch"]]),
    ("Which message broker does the notification service use now?", "Kafka, topic notifications.v2 (since Sept 2024).",
     "notify_broker", [["notifications.v2"]]),
    ("What is the current database connection pool size for inventory-service?", "50 (raised from 20 in April 2025; PgBouncer default_pool_size 60).",
     "inventory_pool", [["20 to 50"]]),
    ("What is the current per-client rate limit on the API gateway?", "1500 requests per second (raised from 1000 in June 2025).",
     "gateway_ratelimit", [["1500"]]),
    ("What timeout does checkout use when calling the payment service?", "3 seconds with a single retry (changed Jan 2025 from 5s/2 retries).",
     "checkout_timeout", [["3 second"]]),
    ("Which database engine is the user profile service running on today?", "Aurora MySQL 8 (migration completed Dec 2024).",
     "profile_db", [["aurora"]]),
    ("What time does the nightly invoice generation job run?", "04:30 UTC (moved from 02:00 UTC in July 2025).",
     "billing_cron", [["04:30"]]),
    ("When did the payment service stop using Redis?", "February 2025 (Payments Architecture Sync, 2025-02-12).",
     "payment_redis", [["stopped using redis"]]),
    ("Is the Jenkins order-deploy job still used?", "No, it is disabled; deploys go through ArgoCD since Nov 2024.",
     "order_deploy", [["disabled"]]),
    ("Is the es-search-prod Elasticsearch cluster still running?", "No, it was decommissioned after the OpenSearch migration (March 2025).",
     "search_engine", [["decommissioned"]]),
    ("Do services still accept HS256-signed tokens?", "No. Since May 2025 only RS256 tokens validated via JWKS are accepted.",
     "auth_signing", [["no longer accepted"]]),
    ("Has the API gateway rate limit always been 1500 requests per second?", "No. It was 1000 rps per client (FAQ, Jan 2024) and was raised to 1500 in June 2025.",
     "gateway_ratelimit", [["1500"], ["1000"]]),
]
for q, a, key, kw in T:
    cur = d(f"{key}.new")
    stale = d(f"{key}.old") + F.get(f"{key}.stale", [])
    rel = [cur] if key != "gateway_ratelimit" or "always" not in q else [cur, stale]
    add("temporal", q, a, rel, kw, current=cur[0], stale=stale)

# ---------------------------------------------------------------- multi-document
for q, a, rels, kw in [
    ("What language is the payment service written in, and how do we deploy it?", "Java 17/Spring Boot 3; ArgoCD sync of payment-service-prod.",
     [d("payment-service.lang"), d("payment-service.deploy")], [["java 17"], ["payment-service-prod"]]),
    ("Which team owns the order service and what is the current way to deploy it?", "Orders team; ArgoCD app order-service-prod.",
     [d("order-service.team"), d("order_deploy.new")], [["orders team"], ["order-service-prod"]]),
    ("What port does the auth service listen on and how are its tokens signed today?", "9000; RS256 via Keycloak JWKS.",
     [d("auth-service.port"), d("auth_signing.new")], [["9000"], ["rs256"]]),
    ("If Redis goes down, what happens to checkout, and which team owns checkout?", "Carts fall back to checkout-db; owned by Checkout Experience.",
     [["runbook_redis_outage"], d("checkout-service.team")], [["checkout-db"], ["checkout experience"]]),
    ("What sits between inventory-service and its database, and what is its current pool size?", "PgBouncer; DB_POOL_MAX 50.",
     [d("inventory-service.db"), d("inventory_pool.new")], [["pgbouncer"], ["20 to 50"]]),
    ("Which on-call channel handles notification issues and which topic does the service consume now?", "#engagement-oncall; Kafka notifications.v2.",
     [d("notification-service.oncall"), d("notify_broker.new")], [["#engagement-oncall"], ["notifications.v2"]]),
    ("Who is tech lead of the search service and what engine does it run on now?", "Liam Chen; OpenSearch 2.11.",
     [d("search-service.team") + d("search-service.oncall"), d("search_engine.new")], [["liam chen"], ["opensearch"]]),
    ("What language is the billing service written in and when does its invoice job run now?", "Scala 2.13; 04:30 UTC.",
     [d("billing-service.lang"), d("billing_cron.new")], [["scala"], ["04:30"]]),
    ("Which services use Redis, and what happens to rate limiting if Redis fails?", "checkout-service (carts) and api-gateway (rate-limit counters); the rate limiter fails open.",
     [["faq_platform", "arch_platform_overview"], ["runbook_redis_outage"]], [["rate-limit counters"], ["fails open"]]),
    ("How does the checkout service authenticate requests and what timeout does it use for payment calls?", "JWTs validated at gateway, forwarded as X-User-Context; 3 second timeout.",
     [d("checkout-service.auth"), d("checkout_timeout.new")], [["x-user-context"], ["3 second"]]),
    ("What is the user profile service's health endpoint and which DB engine does it run on now?", "/actuator/health; Aurora MySQL 8.",
     [d("user-profile-service.health"), d("profile_db.new")], [["/actuator/health"], ["aurora"]]),
    ("Which team owns the API gateway and what is its current rate limit?", "Platform Edge; 1500 rps per client.",
     [d("api-gateway.team") + ["faq_gateway"], d("gateway_ratelimit.new")], [["platform edge"], ["1500"]]),
    ("What port does the payment service use and where are payment sessions stored now?", "8443; PostgreSQL payment_sessions table.",
     [d("payment-service.port"), d("payment_redis.new")], [["8443"], ["payment_sessions"]]),
    ("What is the shipping service written in and what should I check when label generation fails?", "Python 3.10/Django; carrier API status and labelgen queue depth.",
     [d("shipping-service.lang"), d("shipping-service.runbook")], [["python 3.10"], ["labelgen queue"]]),
    ("How do I deploy the notification service and which provider sends its emails?", "Sync ArgoCD app notification-service-prod; SendGrid.",
     [d("notification-service.deploy"), d("notification-service.lang") + d("notification-service.runbook")], [["notification-service-prod"], ["sendgrid"]]),
]:
    add("multi_doc", q, a, rels, kw)

# ---------------------------------------------------------------- sparse
for q, a, key, kw in [
    ("How many days before expiry does the TLS certificate alert fire?", "21 days.", "tls_alert", ["21 days"]),
    ("What is the feature flag for enforcing 3-D Secure?", "pay.3ds.enforce (off in staging).", "3ds_flag", ["pay.3ds.enforce"]),
    ("When are staging database snapshots refreshed?", "Every Sunday at 03:00 UTC.", "staging_refresh", ["sunday at 03:00"]),
    ("Where are the k6 load test scripts kept?", "perf-tests repo, scenarios/checkout.", "k6_repo", ["perf-tests"]),
    ("How long before PagerDuty escalates to the secondary on-call?", "15 minutes without an ack.", "pd_escalation", ["15 minutes without an ack"]),
    ("Which Grafana dashboard should I use for checkout?", "CHK-OVERVIEW.", "grafana_chk", ["chk-overview"]),
    ("What is the maximum avatar upload size?", "5 MB (larger returns 413).", "avatar_size", ["5 mb"]),
    ("How often are database credentials rotated?", "Every 90 days by Vault (secret/data/db-creds).", "vault_rotation", ["90 days"]),
    ("When does the deploy freeze start?", "Friday 14:00 IST until Monday.", "deploy_freeze", ["14:00 ist"]),
    ("What canary percentage and duration does Argo Rollouts use?", "10 percent of traffic for 20 minutes.", "canary", ["10 percent"]),
    ("How long is data retained on the payments.events Kafka topic?", "7 days; older replays need the S3 archive.", "kafka_retention", ["7 days"]),
    ("What Spark version does the nightly analytics batch use?", "Spark 3.4 on EMR (analytics-batch).", "spark_emr", ["spark 3.4"]),
    ("What renders shipping labels?", "labelgen, which outputs PDF via wkhtmltopdf.", "labelgen", ["wkhtmltopdf"]),
    ("How long until an unconfirmed inventory reservation expires?", "15 minutes.", "reservation_ttl", ["expire after 15 minutes"]),
    ("Which WAF rule set does the gateway run?", "OWASP CRS 4 in blocking mode.", "waf_rules", ["owasp crs 4"]),
]:
    add("sparse", q, a, [d(f"sparse.{key}")], [kw])

# ---------------------------------------------------------------- no-answer
for q in [
    "What GPU instance type does the recommendation service use?",
    "When is the payment service's next PCI DSS audit?",
    "Which CDN provider serves our static assets?",
    "What is the monthly AWS cost of the search cluster?",
    "What is the database connection pool size for the shipping service?",
    "Which mobile app version introduced biometric login?",
    "What uptime SLA do we promise enterprise customers for the billing API?",
    "Who approved moving the notification service to Kafka?",
    "What eviction policy is configured on checkout-redis?",
    "What port does the fraud-detection service listen on?",
    "How do we publish the iOS app to the App Store?",
    "What is the disaster recovery RTO for orders-db?",
    "Which vendor provides our SIEM?",
    "What programming language is the loyalty-points service written in?",
    "What is the on-call channel for the machine learning platform team?",
]:
    add("no_answer", q, "Not in the knowledge base.", [], [])

out = ROOT / "eval" / "questions.json"
out.write_text(json.dumps(Q, indent=1))
from collections import Counter
print(len(Q), Counter(x["category"] for x in Q))
