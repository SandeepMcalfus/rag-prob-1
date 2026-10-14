"""Single source of truth for the synthetic corpus.

Every fact that a test question depends on lives here, so the generated
documents and the ground-truth answers can never drift apart.
"""

SERVICES = {
    "payment-service": dict(
        name="Payment Service", team="Payments Core", lang="Java 17 with Spring Boot 3",
        port=8443, db="PostgreSQL 14 cluster payments-db", health="/actuator/health",
        oncall="#payments-oncall", argo="payment-service-prod", chart="charts/payment-service",
        auth="mutual TLS (mTLS) between services plus OAuth2 client-credentials tokens issued by auth-service",
        deps=["api-gateway", "auth-service", "payments-db", "Stripe and Adyen payment providers"],
        lead="Priya Nair",
    ),
    "checkout-service": dict(
        name="Checkout Service", team="Checkout Experience", lang="Node.js 20 with NestJS",
        port=8080, db="carts cached in Redis (checkout-redis) with PostgreSQL checkout-db as the system of record",
        health="/healthz", oncall="#checkout-oncall", argo="checkout-service-prod", chart="charts/checkout-service",
        auth="JWT bearer tokens validated at the api-gateway, forwarded as the X-User-Context header",
        deps=["payment-service", "inventory-service", "checkout-redis", "checkout-db"],
        lead="Daniel Okafor",
    ),
    "auth-service": dict(
        name="Auth Service", team="Identity Platform", lang="Go 1.22",
        port=9000, db="PostgreSQL identity-db", health="/health/ready",
        oncall="#identity-oncall", argo="auth-service-prod", chart="charts/auth-service",
        auth="issues the tokens other services use; see token signing notes",
        deps=["identity-db", "Keycloak realm acme-prod"],
        lead="Sofia Marquez",
    ),
    "user-profile-service": dict(
        name="User Profile Service", team="Customer Data", lang="Kotlin on Ktor",
        port=8081, db="see data store notes", health="/actuator/health",
        oncall="#customer-data-oncall", argo="user-profile-service-prod", chart="charts/user-profile-service",
        auth="JWT bearer tokens validated at the api-gateway",
        deps=["auth-service", "profile-db", "S3 bucket acme-avatars"],
        lead="Hannah Weber",
    ),
    "notification-service": dict(
        name="Notification Service", team="Engagement", lang="Python 3.11 with FastAPI",
        port=8090, db="PostgreSQL notify-db for templates and delivery logs", health="/healthz",
        oncall="#engagement-oncall", argo="notification-service-prod", chart="charts/notification-service",
        auth="internal-only; mTLS from callers",
        deps=["SendGrid (email)", "Twilio (SMS)", "message broker"],
        lead="Arjun Mehta",
    ),
    "search-service": dict(
        name="Search Service", team="Discovery", lang="Java 21",
        port=8200, db="search cluster (see engine notes)", health="/actuator/health",
        oncall="#discovery-oncall", argo="search-service-prod", chart="charts/search-service",
        auth="JWT bearer tokens validated at the api-gateway; anonymous search allowed",
        deps=["search cluster", "inventory-service change feed"],
        lead="Liam Chen",
    ),
    "inventory-service": dict(
        name="Inventory Service", team="Supply Chain", lang="Go 1.21",
        port=8300, db="PostgreSQL inventory-db accessed through PgBouncer", health="/healthz",
        oncall="#supply-oncall", argo="inventory-service-prod", chart="charts/inventory-service",
        auth="mTLS between services",
        deps=["inventory-db", "PgBouncer", "order-service events"],
        lead="Grace Kim",
    ),
    "order-service": dict(
        name="Order Service", team="Orders", lang="Java 17 with Spring Boot 3",
        port=8400, db="PostgreSQL orders-db with a transactional outbox table", health="/actuator/health",
        oncall="#orders-oncall", argo="order-service-prod", chart="charts/order-service",
        auth="mTLS between services plus OAuth2 client-credentials tokens",
        deps=["payment-service", "inventory-service", "orders-db", "Kafka topic orders.events"],
        lead="Mateo Rossi",
    ),
    "shipping-service": dict(
        name="Shipping Service", team="Logistics", lang="Python 3.10 with Django",
        port=8500, db="PostgreSQL shipping-db", health="/health",
        oncall="#logistics-oncall", argo="shipping-service-prod", chart="charts/shipping-service",
        auth="mTLS between services",
        deps=["order-service events", "FedEx and DHL carrier APIs", "labelgen"],
        lead="Chloe Dubois",
    ),
    "billing-service": dict(
        name="Billing Service", team="Finance Engineering", lang="Scala 2.13 on Akka HTTP",
        port=8600, db="PostgreSQL billing-db", health="/status",
        oncall="#fin-eng-oncall", argo="billing-service-prod", chart="charts/billing-service",
        auth="mTLS between services plus OAuth2 client-credentials tokens",
        deps=["payment-service", "order-service events", "billing-db"],
        lead="Noah Fischer",
    ),
    "analytics-pipeline": dict(
        name="Analytics Pipeline", team="Data Platform", lang="Python and PySpark",
        port=8700, db="Snowflake warehouse ACME_ANALYTICS", health="/ping",
        oncall="#data-platform-oncall", argo="analytics-api-prod", chart="charts/analytics-api",
        auth="service accounts with Snowflake key-pair authentication",
        deps=["Kafka", "Airflow", "Snowflake"],
        lead="Emma Larsen",
    ),
    "api-gateway": dict(
        name="API Gateway", team="Platform Edge", lang="Kong 3.4 with custom Lua plugins",
        port=443, db="Redis (gateway-redis) for rate-limit counters", health="/status/ready",
        oncall="#edge-oncall", argo="api-gateway-prod", chart="charts/api-gateway",
        auth="validates JWTs issued by auth-service on every external request",
        deps=["auth-service", "gateway-redis", "all backend services"],
        lead="Omar Haddad",
    ),
}

# Facts that changed over time. old -> new, each in documents of different dates.
CONFLICTS = {
    "payment_redis": dict(
        old="The Payment Service stores payment sessions in Redis (payments-redis cluster) with a 30 minute TTL.",
        new="We stopped using Redis for the payment service in February; payment sessions now live in the PostgreSQL table payment_sessions in payments-db.",
        old_date="2024-01-15", new_date="2025-02-12",
    ),
    "auth_signing": dict(
        old="Access tokens are JWTs signed with HS256 using a shared secret distributed via Vault.",
        new="Token signing has moved to RS256 with keys managed by Keycloak; services must validate tokens against the JWKS endpoint https://auth.acme.internal/realms/acme-prod/protocol/openid-connect/certs. HS256 shared-secret tokens are no longer accepted.",
        old_date="2023-11-02", new_date="2025-05-06",
    ),
    "order_deploy": dict(
        old="Order Service is deployed with the Jenkins job order-deploy (parameter ENV=prod).",
        new="Order Service deployments moved off Jenkins to ArgoCD; production deploys are done by syncing the ArgoCD application order-service-prod. The Jenkins job order-deploy is disabled.",
        old_date="2024-03-08", new_date="2024-11-20",
    ),
    "search_engine": dict(
        old="Search Service runs on Elasticsearch 7.10 (cluster es-search-prod).",
        new="The search cluster migration is done: Search Service now runs on OpenSearch 2.11 (cluster os-search-prod) and es-search-prod is decommissioned.",
        old_date="2023-09-18", new_date="2025-03-04",
    ),
    "notify_broker": dict(
        old="Notification Service consumes jobs from RabbitMQ (exchange notify.jobs).",
        new="Notification Service has switched from RabbitMQ to Kafka; it now consumes the Kafka topic notifications.v2 with consumer group notification-workers.",
        old_date="2024-02-14", new_date="2024-09-17",
    ),
    "inventory_pool": dict(
        old="inventory-service DB connection pool size is 20 (DB_POOL_MAX=20).",
        new="We bumped inventory-service DB_POOL_MAX from 20 to 50 after the pool exhaustion alerts; PgBouncer default_pool_size raised to 60 to match.",
        old_date=None, new_date="2025-04-08",
    ),
    "gateway_ratelimit": dict(
        old="The API Gateway rate limit is 1000 requests per second per client.",
        new="Agreed: we raise the per-client rate limit on the API Gateway from 1000 to 1500 requests per second, effective this sprint.",
        old_date="2024-01-22", new_date="2025-06-10",
    ),
    "checkout_timeout": dict(
        old="Checkout Service calls the Payment Service with a 5 second timeout and 2 retries.",
        new="Checkout Service now calls the Payment Service with a 3 second timeout and a single retry (changed to reduce tail latency during PSP slowdowns).",
        old_date="2024-01-15", new_date="2025-01-15",
    ),
    "profile_db": dict(
        old="User Profile Service stores profiles in self-managed MySQL 5.7 (profile-db).",
        new="profile-db migration to Aurora MySQL 8 completed tonight; User Profile Service is fully on Aurora now and the MySQL 5.7 hosts are scheduled for teardown.",
        old_date="2023-06-12", new_date="2024-12-02",
    ),
    "billing_cron": dict(
        old="The nightly invoice generation job runs at 02:00 UTC.",
        new="We're moving the nightly invoice generation job from 02:00 UTC to 04:30 UTC so it doesn't overlap the warehouse load.",
        old_date="2024-05-20", new_date="2025-07-21",
    ),
}

# Facts mentioned exactly once, buried in chatter (sparse-data category).
SPARSE = {
    "tls_alert": "fyi the TLS cert expiry alert fires 21 days before expiry now, not 7",
    "3ds_flag": "the feature flag for enforcing 3-D Secure is pay.3ds.enforce, it's off in staging",
    "staging_refresh": "staging DB snapshots refresh every Sunday at 03:00 UTC, so don't rely on staging data persisting past the weekend",
    "k6_repo": "the k6 load test scripts live in the perf-tests repo under scenarios/checkout",
    "pd_escalation": "PagerDuty escalates to the secondary on-call after 15 minutes without an ack",
    "grafana_chk": "the checkout dashboard you want is CHK-OVERVIEW in Grafana",
    "avatar_size": "max avatar upload size is 5 MB, anything bigger gets a 413 from user-profile-service",
    "vault_rotation": "database credentials are rotated every 90 days by Vault, the path is secret/data/db-creds",
    "deploy_freeze": "reminder: deploy freeze starts Friday 14:00 IST, nothing to prod until Monday",
    "canary": "Argo Rollouts canary is 10 percent of traffic for 20 minutes before full promotion",
    "kafka_retention": "retention on payments.events is 7 days, so replays older than that need the S3 archive",
    "spark_emr": "the nightly batch runs Spark 3.4 on EMR, cluster name analytics-batch",
    "labelgen": "shipping labels are rendered by a small service called labelgen that outputs PDF via wkhtmltopdf",
    "reservation_ttl": "inventory reservations expire after 15 minutes if checkout doesn't confirm",
    "waf_rules": "the gateway WAF is running the OWASP CRS 4 rule set in blocking mode",
}

PEOPLE = [
    "Priya Nair", "Daniel Okafor", "Sofia Marquez", "Hannah Weber", "Arjun Mehta", "Liam Chen",
    "Grace Kim", "Mateo Rossi", "Chloe Dubois", "Noah Fischer", "Emma Larsen", "Omar Haddad",
    "Marcus Lee", "Aisha Bello", "Ravi Kulkarni", "Julia Novak", "Ken Tanaka", "Fatima Zahra",
]
