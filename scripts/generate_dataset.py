"""Generate a deliberately messy engineering knowledge base.

Output: data/raw/<type>/... plus data/manifest.json (true dates + where each
evaluated fact was planted). The manifest is ONLY used by the evaluation
harness - the RAG pipeline never reads it.

    python scripts/generate_dataset.py --scale 1
"""
import argparse
import json
import random
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from facts import CONFLICTS, PEOPLE, SERVICES, SPARSE

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
rng = random.Random(42)
MANIFEST = {"documents": {}, "facts": {}}


def register(doc_id, path, source_type, date, title):
    MANIFEST["documents"][doc_id] = dict(path=str(path.relative_to(ROOT)), source_type=source_type,
                                         true_date=date, title=title)


def plant(fact_key, doc_id):
    MANIFEST["facts"].setdefault(fact_key, []).append(doc_id)


# ----------------------------------------------------------------------------- filler
GENERIC = [
    "We should revisit the alert thresholds after the next game day.",
    "The dashboards were updated to show saturation alongside latency and errors.",
    "Remember to tag pull requests with the owning team so reviews get routed correctly.",
    "Flaky integration tests in CI are tracked on the quality board; please do not just re-run them.",
    "Capacity planning for the holiday peak starts in September every year.",
    "All services must expose Prometheus metrics on the /metrics path.",
    "Structured JSON logging is mandatory; free-text logs are dropped by the log pipeline.",
    "Feature work is paused during incident follow-up weeks until action items are closed.",
    "Service-level objectives are reviewed quarterly with product owners.",
    "Infrastructure changes go through Terraform plans that need two approvals.",
    "Staging mirrors production topology but runs at roughly one tenth of the capacity.",
    "Container images are built once and promoted across environments by digest.",
    "Every service has a README that links to its dashboards and runbook.",
    "Secrets must never be committed; the pre-commit hook scans for high-entropy strings.",
    "Load tests should be coordinated in the platform channel so they do not trip alerts.",
    "Dependency upgrades are batched weekly by the platform bot.",
    "Tracing uses OpenTelemetry with a ten percent head-based sampling rate.",
    "Database schema migrations must be backward compatible for at least one release.",
    "Postmortems are blameless and are published within five business days.",
    "On-call handover happens every Monday at 10:00 local time.",
]
CHAT = [
    "anyone else seeing slow CI today?", "lgtm :+1:", "taking a look", "can we sync after standup?",
    "ack", "same as last week I think", "ok merged", "see above", "yeah that's the one",
    "not sure, ask in the platform channel", "dashboards look fine on my side", "rolling back just in case",
    "false alarm, it was the synthetic check", "thanks!", ":eyes:", "will do after lunch",
    "is staging down again?", "nope, just slow", "ticket filed", "+1", "can someone review my PR",
    "we discussed this in the arch sync", "let's not do that on a Friday", "done", "hmm interesting",
]
SPOKEN = [
    "Okay, um, so let's get started.", "Can everyone hear me? Yeah, okay.",
    "Sorry, I was on mute.", "I think we covered that last time, right?",
    "Let's take that offline.", "Uh, I'll share my screen.", "Is that a hard requirement or a nice-to-have?",
    "We're slightly over time so let's move on.", "Can you put that in the notes?",
    "I don't have context on that one, sorry.", "Makes sense to me.", "[crosstalk]",
    "Let me check the dashboard real quick.", "That's a good question, I'm not sure.",
    "We had a similar discussion in Q3.", "Okay, any other updates?", "Nothing from my side.",
]


def filler(n):
    return " ".join(rng.choice(GENERIC) for _ in range(n))


# ----------------------------------------------------------------------------- PDFs
def pdf(path, title, date, sections, doc_id):
    """sections: list of (heading, [paragraph, ...])"""
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]),
             Paragraph(f"Document date: {date} &nbsp;&nbsp; Classification: Internal", styles["Normal"]),
             Spacer(1, 12), Paragraph("Table of Contents", styles["Heading2"])]
    for i, (h, _) in enumerate(sections, 1):
        story.append(Paragraph(f"{i}. {h} ........................ {i + 1}", styles["Normal"]))
    story.append(PageBreak())
    for i, (h, paras) in enumerate(sections, 1):
        story.append(Paragraph(f"{i}. {h}", styles["Heading1"]))
        for p in paras:
            story.append(Paragraph(p, styles["BodyText"]))
            story.append(Spacer(1, 6))

    def deco(canvas, doc):  # repeated header/footer noise on every page
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "ACME Corp Engineering  |  INTERNAL - DO NOT DISTRIBUTE")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, title[:60])
        canvas.drawString(2 * cm, 1.2 * cm, f"Page {doc.page}  |  Generated from Confluence export")
        canvas.restoreState()

    SimpleDocTemplate(str(path), pagesize=A4, title=title).build(story, onFirstPage=deco, onLaterPages=deco)
    register(doc_id, path, "pdf", date, title)


ARCH_DATES = {
    "payment-service": "2024-01-15", "checkout-service": "2024-01-15", "auth-service": "2024-06-03",
    "user-profile-service": "2023-06-12", "notification-service": "2024-02-01", "search-service": "2023-09-18",
    "inventory-service": "2024-04-22", "order-service": "2024-03-01", "shipping-service": "2023-12-05",
    "billing-service": "2024-05-02", "analytics-pipeline": "2024-07-15", "api-gateway": "2024-01-22",
}


def gen_arch_pdfs():
    for key, s in SERVICES.items():
        doc_id = f"arch_{key}"
        overview = [f"The {s['name']} ({key}) is owned by the {s['team']} team, with {s['lead']} as technical lead. "
                    f"It is implemented in {s['lang']} and listens on port {s['port']}. " + filler(3),
                    filler(4)]
        data = [f"Primary data store: {s['db']}. " + filler(2)]
        if key == "payment-service":
            data.append(CONFLICTS["payment_redis"]["old"] + " Session keys follow the pattern pay:sess:{id}.")
            plant("payment_redis.old", doc_id)
        if key == "search-service":
            data.append(CONFLICTS["search_engine"]["old"] + " Index refresh interval is one second.")
            plant("search_engine.old", doc_id)
        if key == "user-profile-service":
            data.append(CONFLICTS["profile_db"]["old"] + " Read replicas serve profile lookups.")
            plant("profile_db.old", doc_id)
        deps = [f"{s['name']} depends on: " + ", ".join(s["deps"]) + ". " + filler(2)]
        if key == "checkout-service":
            deps.append(CONFLICTS["checkout_timeout"]["old"])
            plant("checkout_timeout.old", doc_id)
        sec = [f"Authentication mechanism: {s['name']} uses {s['auth']}. " + filler(2)]
        sections = [("Overview", overview), ("Data Stores", data), ("Dependencies", deps),
                    ("Security and Authentication", sec), ("Scaling", [filler(5), filler(4)]),
                    ("Open Questions", [filler(3)])]
        pdf(RAW / "pdf" / f"{doc_id}.pdf", f"{s['name']} Architecture", ARCH_DATES[key], sections, doc_id)
        for f in ("team", "lang", "port", "auth", "db"):
            plant(f"{key}.{f}", doc_id)

    # two platform-wide PDFs
    pdf(RAW / "pdf" / "arch_platform_overview.pdf", "Platform Architecture Overview", "2024-02-10",
        [("Topology", [f"The platform runs {len(SERVICES)} core services on Kubernetes (EKS) in eu-west-1. " + filler(5)]),
         ("Request Flow", ["External traffic enters through the API Gateway, which validates JWTs and applies "
                           "rate limits before routing to backend services. " + filler(4)]),
         ("Caching", ["Redis is used by checkout-service for carts and by api-gateway for rate-limit counters. " + filler(3)]),
         ("Observability", [filler(6)])], "arch_platform_overview")
    pdf(RAW / "pdf" / "arch_data_platform.pdf", "Data Platform Design", "2024-07-15",
        [("Ingestion", ["Events flow from Kafka into Snowflake via the analytics pipeline. " + filler(4)]),
         ("Orchestration", ["Airflow schedules batch jobs. " + filler(4)]),
         ("Governance", [filler(5)])], "arch_data_platform")


# ----------------------------------------------------------------------------- Markdown
SVC_MD_DATES = {k: d for k, d in zip(SERVICES, ["2024-10-01", "2025-01-15", "2024-08-12", "2024-06-30",
                                                 "2024-02-14", "2024-05-09", "2024-09-23", "2024-07-07",
                                                 "2024-04-18", "2024-03-27", "2024-11-11", "2024-06-01"])}


def write_md(path, front, body, doc_id, date, title, source_type="markdown"):
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = "---\n" + "".join(f"{k}: {v}\n" for k, v in front.items()) + "---\n\n" if front else ""
    path.write_text(fm + body)
    register(doc_id, path, source_type, date, title)


def gen_service_md():
    for key, s in SERVICES.items():
        doc_id = f"svc_{key}"
        date = SVC_MD_DATES[key]
        extra = ""
        if key == "checkout-service":
            extra = "\n### Payment client settings\n\n" + CONFLICTS["checkout_timeout"]["new"] + "\n"
            plant("checkout_timeout.new", doc_id)
        if key == "notification-service":
            extra = "\n### Messaging\n\n" + CONFLICTS["notify_broker"]["old"] + " Dead letters go to notify.dlq.\n"
            plant("notify_broker.old", doc_id)
        if key == "payment-service":
            extra = "\n### Release strategy\n\nProduction uses Argo Rollouts canary releases with automated analysis on error rate.\n"
        body = f"""# {s['name']}

Owner: **{s['team']}** · Tech lead: {s['lead']}

{filler(3)}

## Deployment

To deploy {key} to production, merge to `main`; CI builds the image and bumps the image tag in
`{s['chart']}/values-prod.yaml`. Then sync the ArgoCD application `{s['argo']}`
(`argocd app sync {s['argo']}`) and watch the rollout in the ArgoCD UI.
{extra}
## Health checks

Liveness and readiness probes hit `{s['health']}`. {filler(1)}

## On-call

Page the on-call engineer via PagerDuty service "{s['name']}". Discussion happens in `{s['oncall']}`.

## Notes

{filler(4)}
"""
        if key == "order-service":  # stale deploy instructions are in the runbook; svc page predates migration note
            body = body.replace(f"Then sync the ArgoCD application `{s['argo']}`\n(`argocd app sync {s['argo']}`) and watch the rollout in the ArgoCD UI.",
                                "Deployment steps are described in the order-service runbook.")
        write_md(RAW / "markdown" / f"{doc_id}.md", {"title": s["name"], "owner": s["team"], "last_updated": date},
                 body, doc_id, date, s["name"])
        for f in ("team", "deploy", "health", "oncall"):
            if not (key == "order-service" and f == "deploy"):
                plant(f"{key}.{f}", doc_id)


def gen_misc_md(scale):
    # conflict carriers
    write_md(RAW / "markdown" / "auth_token_design.md", {"title": "Auth Token Design", "last_updated": "2023-11-02"},
             f"# Auth Token Design\n\n## Token format\n\n{CONFLICTS['auth_signing']['old']} Tokens expire after 15 minutes "
             f"and refresh tokens after 7 days.\n\n## Rationale\n\n{filler(4)}\n",
             "auth_token_design", "2023-11-02", "Auth Token Design")
    plant("auth_signing.old", "auth_token_design")
    write_md(RAW / "markdown" / "order_service_argocd_migration.md",
             {"title": "Order Service: Jenkins to ArgoCD migration", "last_updated": "2024-11-20"},
             f"# Order Service: Jenkins to ArgoCD migration\n\n## Status\n\nComplete.\n\n## Summary\n\n"
             f"{CONFLICTS['order_deploy']['new']} To deploy: merge to main, then run `argocd app sync order-service-prod`.\n\n"
             f"## Follow-ups\n\n{filler(3)}\n", "order_service_argocd_migration", "2024-11-20",
             "Order Service: Jenkins to ArgoCD migration")
    plant("order_deploy.new", "order_service_argocd_migration")
    plant("order-service.deploy", "order_service_argocd_migration")

    topics = [
        ("onboarding", "Engineering Onboarding"), ("coding_standards", "Coding Standards"),
        ("adr_001_kubernetes", "ADR 001: Adopt Kubernetes"), ("adr_002_kafka", "ADR 002: Kafka as event backbone"),
        ("adr_003_argocd", "ADR 003: GitOps with ArgoCD"), ("adr_004_opentelemetry", "ADR 004: OpenTelemetry"),
        ("observability_guide", "Observability Guide"), ("ci_pipeline", "CI Pipeline Guide"),
        ("local_dev_setup", "Local Development Setup"), ("code_review_guidelines", "Code Review Guidelines"),
        ("incident_severity_levels", "Incident Severity Levels"), ("terraform_conventions", "Terraform Conventions"),
        ("api_design_guidelines", "API Design Guidelines"), ("database_migrations", "Database Migration Policy"),
        ("release_calendar", "Release Calendar"), ("security_baseline", "Security Baseline"),
    ]
    for i, (slug, title) in enumerate(topics * scale):
        sid = slug if i < len(topics) else f"{slug}_v{i // len(topics) + 1}"
        date = f"202{3 + i % 3}-{(i % 12) + 1:02d}-{(i * 7) % 27 + 1:02d}"
        body = f"# {title}\n\n{filler(3)}\n\n## Background\n\n{filler(5)}\n\n## Guidance\n\n" + \
               "\n".join(f"- {rng.choice(GENERIC)}" for _ in range(6)) + f"\n\n## FAQ\n\n{filler(3)}\n"
        write_md(RAW / "markdown" / f"{sid}.md", {"title": title, "last_updated": date}, body, sid, date, title)


# ----------------------------------------------------------------------------- Runbooks
def gen_runbooks():
    procedures = {
        "payment-service": ("Payment provider timeouts", "If Stripe or Adyen calls time out, check the PSP status pages, "
                            "then confirm the circuit breaker state on the payment dashboard. If the breaker is open, "
                            "traffic is automatically failed over to the secondary PSP; do not restart pods."),
        "checkout-service": ("Cart errors", "If carts fail to load, check checkout-redis health. Checkout falls back to "
                             "reading carts from checkout-db automatically; expect higher latency but no data loss."),
        "auth-service": ("Users cannot log in", "If logins fail globally, check Keycloak realm acme-prod health and the "
                         "identity-db connection count. Restarting auth-service pods is safe; tokens are stateless."),
        "user-profile-service": ("Profile updates failing", "Check replication lag on profile-db and the S3 bucket "
                                 "acme-avatars permissions. Writes are retried by the client for 60 seconds."),
        "notification-service": ("Emails or SMS not delivered", "Check the SendGrid and Twilio status pages, then the "
                                 "consumer lag of the notification workers. Undelivered messages are retried with "
                                 "exponential backoff for 24 hours."),
        "search-service": ("Search results stale or missing", "Trigger a reindex with the reindex-products job in Airflow "
                           "and verify the change feed consumer is not lagging."),
        "inventory-service": ("Stock counts wrong", "Run the reconcile-stock job, which compares reservations with "
                              "order-service events and repairs drift."),
        "order-service": ("Orders stuck in PENDING", "Check the outbox relay; if the relay is stuck, restart the "
                          "outbox-relay deployment. Orders are reprocessed idempotently."),
        "shipping-service": ("Label generation failures", "Check carrier API status for FedEx and DHL and the labelgen "
                             "queue depth; failed labels can be regenerated from the admin console."),
        "billing-service": ("Invoices not generated", "Check the invoice job logs in Airflow and rerun for the missing "
                            "date range with the --backfill flag."),
        "analytics-pipeline": ("Dashboards show stale data", "Check the Airflow DAG run history and Snowflake warehouse "
                               "credits; clear and rerun failed tasks."),
        "api-gateway": ("Spike in 429 responses", "Check whether a single client is hitting the per-client rate limit; "
                        "temporary overrides are configured in the Kong consumer config."),
    }
    undated = {"payment-service", "inventory-service", "shipping-service", "analytics-pipeline"}
    for key, s in SERVICES.items():
        doc_id = f"runbook_{key}"
        date = None if key in undated else f"2024-{rng.randint(1, 9):02d}-{rng.randint(1, 27):02d}"
        extra = ""
        if key == "payment-service":
            extra = ("\n## Session issues\n\nPayment sessions are stored in Redis (payments-redis). If customers report "
                     "lost payment sessions, check payments-redis memory usage and evictions with `redis-cli INFO memory`.\n")
            plant("payment_redis.stale", doc_id)
        if key == "inventory-service":
            extra = f"\n## Configuration\n\n{CONFLICTS['inventory_pool']['old']}\n"
            plant("inventory_pool.old", doc_id)
        if key == "order-service":
            date = "2024-03-08"
            extra = f"\n## Deploying\n\n{CONFLICTS['order_deploy']['old']} Wait for the smoke tests stage to pass.\n"
            plant("order_deploy.old", doc_id)
        if key == "billing-service":
            date = "2024-05-20"
            extra = f"\n## Schedules\n\n{CONFLICTS['billing_cron']['old']}\n"
            plant("billing_cron.old", doc_id)
        title, proc = procedures[key]
        front = {"title": f"{s['name']} Runbook"}
        if date:
            front["last_updated"] = date
        body = f"# {s['name']} Runbook\n\n## {title}\n\n{proc}\n{extra}\n## Escalation\n\nEscalate in `{s['oncall']}`. {filler(2)}\n"
        write_md(RAW / "runbooks" / f"{doc_id}.md", front, body, doc_id, date, f"{s['name']} Runbook", "runbook")
        plant(f"{key}.runbook", doc_id)

    generic = {
        "runbook_redis_outage": ("Redis Outage", None,
            "## Impact\n\nIf Redis goes down, checkout-service falls back to reading carts from checkout-db (higher latency, "
            "no data loss) and the api-gateway rate limiter fails open, meaning rate limits are not enforced until Redis "
            "recovers.\n\n## Actions\n\n1. Confirm the outage on the Redis dashboard.\n2. Check ElastiCache events for failover.\n"
            "3. If failover does not complete within 5 minutes, page the Platform Edge on-call.\n4. Watch for abusive "
            "traffic while the rate limiter is failing open.\n"),
        "runbook_db_connection_failures": ("Database Connection Failures", "2024-08-30",
            "## Symptoms\n\nErrors like `FATAL: remaining connection slots are reserved` or `connection refused` in service logs.\n\n"
            "## Troubleshooting\n\n1. Check PgBouncer with `SHOW POOLS;` and look for waiting clients (cl_waiting > 0).\n"
            "2. Check whether the service connection pool is exhausted (pool metrics on the service dashboard).\n"
            "3. Verify the security group still allows traffic from the EKS node group.\n"
            "4. Check whether Vault rotated the credentials and pods hold stale ones; a rolling restart picks up new credentials.\n"
            "5. Look for long-running transactions with `pg_stat_activity` and terminate them if safe.\n"),
        "runbook_k8s_crashloop": ("Pod CrashLoopBackOff", "2024-04-11",
            "## Steps\n\n1. `kubectl describe pod` to read the last state.\n2. `kubectl logs --previous` for the crash output.\n"
            "3. Check for OOMKilled and raise memory limits in the chart values if needed.\n4. Roll back with ArgoCD history if a deploy caused it.\n"),
        "runbook_incident_process": ("Incident Response Process", "2024-01-05",
            "## Roles\n\nIncident commander, communications lead, scribe.\n\n## Process\n\n1. Declare the incident in #incidents.\n"
            "2. Assign severity using the severity guide.\n3. Post status updates every 30 minutes for SEV1.\n4. Write a postmortem within five business days.\n"),
    }
    for doc_id, (title, date, text) in generic.items():
        front = {"title": title}
        if date:
            front["last_updated"] = date
        write_md(RAW / "runbooks" / f"{doc_id}.md", front, f"# {title}\n\n{text}\n{filler(2)}\n", doc_id, date, title, "runbook")


# ----------------------------------------------------------------------------- FAQ (HTML)
def gen_faq():
    pages = {
        "faq_platform": ("Platform FAQ", "2024-06-14", [
            ("Which cloud region do we run in?", "Production runs in AWS eu-west-1 on EKS."),
            ("Where do I find service dashboards?", "Each service README links to its Grafana dashboards."),
            ("How do I get production access?", "Request the prod-readonly role through the access portal; write access needs a manager approval."),
            ("Which services use Redis?", "checkout-service (carts) and api-gateway (rate-limit counters)."),
        ]),
        "faq_auth": ("Authentication FAQ", "2024-02-20", [
            ("How are access tokens signed?", "Access tokens are JWTs signed with HS256 using a shared secret distributed via Vault."),
            ("How long do access tokens last?", "15 minutes. Refresh tokens last 7 days."),
            ("Which authentication mechanism does service-to-service traffic use?", "Mutual TLS (mTLS), with OAuth2 client-credentials tokens for services that need caller identity."),
        ]),
        "faq_deploy": ("Deployment FAQ", "2024-09-02", [
            ("How do deployments work?", "We use GitOps: CI bumps the image tag in the Helm chart values and ArgoCD syncs the change."),
            ("Can I deploy on Fridays?", "Low-risk changes only, and only before the freeze window."),
            ("How do I roll back?", "Use ArgoCD history to roll back to the previous synced revision."),
        ]),
        "faq_gateway": ("API Gateway FAQ", "2024-01-22", [
            ("What is the rate limit?", CONFLICTS["gateway_ratelimit"]["old"]),
            ("What happens when a client exceeds the limit?", "The gateway returns HTTP 429 with a Retry-After header."),
            ("Who owns the gateway?", "The Platform Edge team."),
        ]),
    }
    plant("auth_signing.stale", "faq_auth")
    plant("gateway_ratelimit.old", "faq_gateway")
    for doc_id, (title, date, qas) in pages.items():
        items = "\n".join(f"<div class='qa'><h3>{q}</h3><p>{a}</p></div>" for q, a in qas)
        html = f"""<!DOCTYPE html><html><head><title>{title}</title><meta name="last-updated" content="{date}">
<script>window.analytics && analytics.page();</script><style>.nav{{color:#333}}</style></head><body>
<div class="nav">Home | Engineering | Wiki | Search | Log out</div>
<h1>{title}</h1>{items}
<footer>© ACME Corp · Internal wiki · Report an issue with this page</footer></body></html>"""
        p = RAW / "faq" / f"{doc_id}.html"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html)
        register(doc_id, p, "faq", date, title)


# ----------------------------------------------------------------------------- Transcripts
def transcript(doc_id, title, date, plants, n_turns=40, date_style="iso"):
    """plants: list of (speaker, sentence, fact_key)"""
    people = rng.sample(PEOPLE, 4)
    lines = []
    t = 5
    insert_at = sorted(rng.sample(range(5, n_turns - 3), len(plants)))
    pi = 0
    for i in range(n_turns):
        t += rng.randint(8, 60)
        stamp = f"[{t // 3600:02d}:{(t % 3600) // 60:02d}:{t % 60:02d}]"
        if pi < len(plants) and i == insert_at[pi]:
            spk, sent, key = plants[pi]
            lines.append(f"{stamp} {spk}: Um, {sent[0].lower() + sent[1:]}")
            plant(key, doc_id)
            pi += 1
        else:
            spk = rng.choice(people)
            txt = rng.choice(SPOKEN) + (" " + rng.choice(GENERIC) if rng.random() < .6 else "")
            lines.append(f"{stamp} {spk}: {txt}")
    d = datetime.strptime(date, "%Y-%m-%d")
    header_date = date if date_style == "iso" else f"Recorded on {d.day} {d.strftime('%b %Y')}"
    head = (f"Meeting: {title}\nDate: {header_date}\n" if date_style == "iso" else f"Meeting: {title}\n{header_date}\n")
    head += f"Attendees: {', '.join(people)}\nTranscript generated automatically - may contain errors.\n\n"
    p = RAW / "transcripts" / f"{doc_id}.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(head + "\n".join(lines) + "\n")
    register(doc_id, p, "transcript", date, title)


def gen_transcripts(scale):
    C, S = CONFLICTS, SPARSE
    planned = [
        ("transcript_payments_arch_sync_2025-02-12", "Payments Architecture Sync", "2025-02-12",
         [("Priya Nair", C["payment_redis"]["new"], "payment_redis.new")], "iso"),
        ("transcript_discovery_sync_2025-03-04", "Discovery Team Sync", "2025-03-04",
         [("Liam Chen", C["search_engine"]["new"], "search_engine.new")], "text"),
        ("transcript_edge_planning_2025-06-10", "Platform Edge Sprint Planning", "2025-06-10",
         [("Omar Haddad", C["gateway_ratelimit"]["new"], "gateway_ratelimit.new")], "iso"),
        ("transcript_finance_eng_sync_2025-07-21", "Finance Engineering Weekly", "2025-07-21",
         [("Noah Fischer", C["billing_cron"]["new"], "billing_cron.new")], "text"),
        ("transcript_payments_standup_2024-10-03", "Payments Standup", "2024-10-03",
         [("Marcus Lee", "By the way, " + S["3ds_flag"] + ".", "sparse.3ds_flag")], "iso"),
        ("transcript_perf_review_2024-08-19", "Performance Review", "2024-08-19",
         [("Ravi Kulkarni", "Oh and " + S["k6_repo"] + ".", "sparse.k6_repo")], "iso"),
        ("transcript_security_review_2024-11-07", "Security Review", "2024-11-07",
         [("Aisha Bello", "Just so everyone knows, " + S["vault_rotation"] + ".", "sparse.vault_rotation")], "text"),
        ("transcript_release_retro_2024-06-27", "Release Process Retro", "2024-06-27",
         [("Julia Novak", "Quick note, " + S["canary"] + ".", "sparse.canary")], "iso"),
        ("transcript_data_platform_sync_2024-09-12", "Data Platform Sync", "2024-09-12",
         [("Emma Larsen", "Right, " + S["spark_emr"] + ".", "sparse.spark_emr")], "iso"),
        ("transcript_supply_chain_sync_2024-05-15", "Supply Chain Sync", "2024-05-15",
         [("Grace Kim", "Also " + S["reservation_ttl"] + ".", "sparse.reservation_ttl")], "text"),
    ]
    for doc_id, title, date, plants, style in planned:
        transcript(doc_id, title, date, plants, n_turns=rng.randint(40, 70), date_style=style)
    names = ["Architecture Review", "Weekly Standup", "Incident Review", "Quarterly Planning", "Tech Debt Triage",
             "Platform Guild", "Reliability Sync", "Frontend-Backend Sync"]
    for i in range(20 * scale):
        d = datetime(2024, 1, 8) + timedelta(days=rng.randint(0, 560))
        ds = d.strftime("%Y-%m-%d")
        title = rng.choice(names)
        transcript(f"transcript_{title.lower().replace(' ', '_').replace('-', '_')}_{ds}_{i}", title, ds, [],
                   n_turns=rng.randint(40, 90), date_style=rng.choice(["iso", "text"]))


# ----------------------------------------------------------------------------- Slack
USERS = {f"U{1000 + i}": n for i, n in enumerate(PEOPLE)}


def slack(doc_id, channel, date, plants, n_threads=6):
    """plants: list of (sentence, fact_key, as_reply)"""
    base = datetime.strptime(date, "%Y-%m-%d").replace(hour=9, tzinfo=timezone.utc)
    ts = base.timestamp()
    msgs = []
    plant_threads = set(rng.sample(range(n_threads), min(len(plants), n_threads)))
    pi = 0
    uids = list(USERS)
    for th in range(n_threads):
        ts += rng.randint(300, 4000)
        parent_ts = f"{ts:.6f}"
        parent_text = rng.choice(CHAT) if rng.random() < .5 else rng.choice(GENERIC)
        planted = None
        if th in plant_threads and pi < len(plants):
            planted = plants[pi]
            pi += 1
            if not planted[2]:
                parent_text = planted[0]
                plant(planted[1], doc_id)
        msgs.append({"type": "message", "user": rng.choice(uids), "text": parent_text, "ts": parent_ts,
                     "thread_ts": parent_ts, "reply_count": 0})
        n_rep = rng.randint(1, 5)
        rep_idx = rng.randint(0, n_rep - 1)
        for r in range(n_rep):
            ts += rng.randint(20, 900)
            text = rng.choice(CHAT)
            if r == rep_idx and planted and planted[2]:
                text = f"<@{rng.choice(uids)}> {planted[0]}"
                plant(planted[1], doc_id)
            msgs.append({"type": "message", "user": rng.choice(uids), "text": text, "ts": f"{ts:.6f}",
                         "thread_ts": parent_ts})
        msgs[-n_rep - 1]["reply_count"] = n_rep
        if rng.random() < .3:  # top-level message with no thread: context gap
            ts += rng.randint(60, 600)
            msgs.append({"type": "message", "user": rng.choice(uids), "text": rng.choice(CHAT), "ts": f"{ts:.6f}"})
    p = RAW / "slack" / channel / f"{date}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(msgs, indent=1))
    register(doc_id, p, "slack", date, f"#{channel} {date}")


def gen_slack(scale):
    C, S = CONFLICTS, SPARSE
    planned = [
        ("identity", "2025-05-06", [(C["auth_signing"]["new"], "auth_signing.new", False)]),
        ("engagement", "2024-09-17", [(C["notify_broker"]["new"], "notify_broker.new", True)]),
        ("supply-chain", "2025-04-08", [(C["inventory_pool"]["new"], "inventory_pool.new", True)]),
        ("customer-data", "2024-12-02", [(C["profile_db"]["new"], "profile_db.new", False)]),
        ("platform", "2024-10-21", [(S["tls_alert"], "sparse.tls_alert", True)]),
        ("platform", "2024-07-30", [(S["staging_refresh"], "sparse.staging_refresh", True)]),
        ("incidents", "2024-08-05", [(S["pd_escalation"], "sparse.pd_escalation", True)]),
        ("checkout-oncall", "2024-11-14", [(S["grafana_chk"], "sparse.grafana_chk", True)]),
        ("customer-data", "2024-09-03", [(S["avatar_size"], "sparse.avatar_size", True)]),
        ("releases", "2024-12-13", [(S["deploy_freeze"], "sparse.deploy_freeze", False)]),
        ("payments-oncall", "2025-01-22", [(S["kafka_retention"], "sparse.kafka_retention", True)]),
        ("logistics", "2024-06-11", [(S["labelgen"], "sparse.labelgen", True)]),
        ("edge-oncall", "2025-02-27", [(S["waf_rules"], "sparse.waf_rules", True)]),
    ]
    for ch, date, plants in planned:
        slack(f"slack_{ch}_{date}", ch, date, plants, n_threads=rng.randint(5, 9))
    channels = ["platform", "incidents", "releases", "payments-oncall", "checkout-oncall", "identity", "engagement",
                "discovery", "supply-chain", "orders", "logistics", "fin-eng", "data-platform", "edge-oncall", "random-eng"]
    used = {(ch, d) for ch, d, _ in planned}
    n = 0
    while n < 60 * scale:
        ch = rng.choice(channels)
        d = (datetime(2024, 1, 2) + timedelta(days=rng.randint(0, 600))).strftime("%Y-%m-%d")
        if (ch, d) in used:
            continue
        used.add((ch, d))
        slack(f"slack_{ch}_{d}", ch, d, [], n_threads=rng.randint(4, 10))
        n += 1
    (RAW / "slack" / "users.json").write_text(json.dumps([{"id": k, "real_name": v} for k, v in USERS.items()], indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=int, default=1, help="multiplies the number of noise documents")
    args = ap.parse_args()
    t = time.time()
    gen_arch_pdfs(); gen_service_md(); gen_misc_md(args.scale); gen_runbooks(); gen_faq()
    gen_transcripts(args.scale); gen_slack(args.scale)
    (ROOT / "data" / "manifest.json").write_text(json.dumps(MANIFEST, indent=1))
    by = {}
    for d in MANIFEST["documents"].values():
        by[d["source_type"]] = by.get(d["source_type"], 0) + 1
    print(f"generated {len(MANIFEST['documents'])} documents {by} in {time.time() - t:.1f}s")


if __name__ == "__main__":
    main()
